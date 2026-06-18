"""MaatEye — Scan Engine: Orchestrates the entire scanning pipeline."""

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from scanner.utils.config import load_config, get_all_patterns, get_pattern_by_id
from scanner.utils.logger import get_logger
from scanner.fetchers.etherscan import fetch_contract_source
from scanner.fetchers.local import get_contract_from_cache

logger = get_logger(__name__)


# ── Result Models ─────────────────────────────────────────────────────────────


@dataclass
class Vulnerability:
    """A single vulnerability finding."""
    pattern_id: str
    pattern_name: str
    severity: str
    contract: str
    contract_name: str
    description: str
    location: str
    snippet: str
    evidence: str
    confidence: float  # 0.0 - 1.0
    recommendation: str


@dataclass
class ContractResult:
    """Scan results for a single contract."""
    address: str
    contract_name: str
    compiler: str
    source_length: int
    vulnerabilities: list[Vulnerability] = field(default_factory=list)
    error: Optional[str] = None
    scan_time_ms: float = 0.0

    @property
    def vuln_count(self) -> int:
        return len(self.vulnerabilities)

    @property
    def critical_count(self) -> int:
        return sum(1 for v in self.vulnerabilities if v.severity == "critical")

    @property
    def high_count(self) -> int:
        return sum(1 for v in self.vulnerabilities if v.severity == "high")

    @property
    def medium_count(self) -> int:
        return sum(1 for v in self.vulnerabilities if v.severity == "medium")


@dataclass
class ScanResults:
    """Aggregated results from a scan session."""
    total_contracts: int = 0
    total_vulns: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    contracts: dict[str, ContractResult] = field(default_factory=dict)
    scan_time_seconds: float = 0.0
    timestamp: str = ""

    def to_dict(self) -> dict:
        return {
            "tool": "MaatEye",
            "version": "1.0.0-alpha",
            "timestamp": self.timestamp,
            "scan_time_seconds": self.scan_time_seconds,
            "total_contracts": self.total_contracts,
            "total_vulns": self.total_vulns,
            "critical_count": self.critical_count,
            "high_count": self.high_count,
            "medium_count": self.medium_count,
            "low_count": self.low_count,
            "contracts": {
                addr: {
                    "contract_name": c.contract_name or "Unknown",
                    "compiler": c.compiler or "N/A",
                    "source_length": c.source_length,
                    "vuln_count": c.vuln_count,
                    "critical_count": c.critical_count,
                    "high_count": c.high_count,
                    "medium_count": c.medium_count,
                    "error": c.error,
                    "vulnerabilities": [
                        {
                            "pattern_id": v.pattern_id,
                            "pattern_name": v.pattern_name,
                            "severity": v.severity,
                            "description": v.description,
                            "location": v.location,
                            "snippet": v.snippet,
                            "confidence": v.confidence,
                            "recommendation": v.recommendation,
                        }
                        for v in c.vulnerabilities
                    ],
                }
                for addr, c in self.contracts.items()
            },
        }

    def to_markdown(self) -> str:
        lines = [
            "# 👁️⚖️ MaatEye Scan Report\n",
            f"**Timestamp:** {self.timestamp}\n",
            f"**Contracts Scanned:** {self.total_contracts}\n",
            f"**Total Vulnerabilities:** {self.total_vulns}\n",
            f"**🔴 Critical:** {self.critical_count} | "
            f"**🟡 High:** {self.high_count} | "
            f"**🔵 Medium:** {self.medium_count}\n",
            "---\n",
        ]

        for addr, contract in self.contracts.items():
            status = "🔴" if contract.critical_count > 0 else (
                "🟡" if contract.high_count > 0 else (
                    "🔵" if contract.medium_count > 0 else "🟢"))
            lines.append(f"## {status} `{addr}`\n")
            lines.append(f"- **Name:** {contract.contract_name or 'Unknown'}")
            lines.append(f"- **Compiler:** {contract.compiler or 'N/A'}")
            lines.append(f"- **Source Size:** {contract.source_length} bytes")
            lines.append(f"- **Findings:** {contract.vuln_count}\n")

            for v in contract.vulnerabilities:
                emoji = {"critical": "🔴", "high": "🟡", "medium": "🔵", "low": "🟢"}
                lines.append(f"### {emoji.get(v.severity, '⚪')} {v.pattern_name}")
                lines.append(f"- **Pattern:** `{v.pattern_id}`")
                lines.append(f"- **Severity:** {v.severity}")
                lines.append(f"- **Description:** {v.description}")
                lines.append(f"- **Location:** `{v.location}`")
                lines.append(f"- **Confidence:** {v.confidence:.0%}")
                if v.snippet:
                    lines.append(f"- **Snippet:**\n```solidity\n{v.snippet}\n```")
                lines.append(f"- **Recommendation:** {v.recommendation}\n")

            lines.append("---\n")

        return "\n".join(lines)

    def to_text(self) -> str:
        lines = [f"MaatEye Scan Report — {self.timestamp}"]
        lines.append(f"{'='*60}")
        lines.append(f"Contracts: {self.total_contracts}")
        lines.append(f"Vulns: {self.total_vulns} "
                      f"(🔴{self.critical_count} 🟡{self.high_count} 🔵{self.medium_count})")
        lines.append("")

        for addr, c in self.contracts.items():
            vulns_str = f" ({c.vuln_count} vulns)" if c.vuln_count else " ✅"
            lines.append(f"  {addr[:10]}...{addr[-6:]} — {c.contract_name}{vulns_str}")
            for v in c.vulnerabilities:
                lines.append(f"    [{v.severity[0].upper()}] {v.pattern_name}: {v.description[:60]}")

        return "\n".join(lines)


# ── Scan Engine ────────────────────────────────────────────────────────────────


class ScanEngine:
    """Orchestrates the scanning pipeline for smart contracts."""

    def __init__(
        self,
        network: str = "mainnet",
        rpc_endpoint: Optional[str] = None,
        pattern_ids: Optional[list[str]] = None,
        max_workers: int = 5,
    ):
        self.network = network
        self.rpc_endpoint = rpc_endpoint
        self.pattern_ids = pattern_ids
        self.max_workers = max_workers

        # Load configuration
        self.config = load_config()
        self.all_patterns = get_all_patterns(self.config)

        # Filter patterns if specific IDs requested
        if pattern_ids:
            self.active_patterns = {
                pid: self.all_patterns[pid]
                for pid in pattern_ids
                if pid in self.all_patterns
            }
        else:
            self.active_patterns = {
                pid: p for pid, p in self.all_patterns.items()
                if p.get("enabled", True)
            }

        logger.info(f"🧩 Loaded {len(self.active_patterns)} active patterns")

    def scan(self, addresses: list[str]) -> ScanResults:
        """Scan a list of contract addresses."""
        start_time = time.time()
        results = ScanResults(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._scan_single, addr): addr
                for addr in addresses
            }

            for future in as_completed(futures):
                addr = futures[future]
                try:
                    result = future.result()
                    results.contracts[addr] = result
                except Exception as e:
                    logger.error(f"❌ Error scanning {addr}: {e}")
                    results.contracts[addr] = ContractResult(
                        address=addr,
                        contract_name="",
                        compiler="",
                        source_length=0,
                        error=str(e),
                    )

        # Aggregate stats
        results.total_contracts = len(results.contracts)
        results.scan_time_seconds = round(time.time() - start_time, 2)

        for c in results.contracts.values():
            results.total_vulns += c.vuln_count
            results.critical_count += c.critical_count
            results.high_count += c.high_count
            results.medium_count += c.medium_count

        logger.info(f"✅ Scan complete: {results.total_contracts} contracts, "
                     f"{results.total_vulns} vulns in {results.scan_time_seconds:.1f}s")

        return results

    def _scan_single(self, address: str) -> ContractResult:
        """Scan a single contract address."""
        t0 = time.time()
        logger.debug(f"  🔍 Scanning {address}...")

        # Fetch source code
        source_data = self._fetch_source(address)
        if "error" in source_data:
            elapsed = (time.time() - t0) * 1000
            return ContractResult(
                address=address,
                contract_name="",
                compiler="",
                source_length=0,
                error=source_data["error"],
                scan_time_ms=elapsed,
            )

        source_code = source_data.get("source_code", "")
        contract_name = source_data.get("contract_name", "")
        compiler = source_data.get("compiler", "")

        result = ContractResult(
            address=address,
            contract_name=contract_name,
            compiler=compiler,
            source_length=len(source_code),
        )

        # Run all patterns against the source
        vulnerabilities = []
        for pid, pattern in self.active_patterns.items():
            try:
                self._apply_pattern(
                    result, pattern, source_code, address, vulnerabilities
                )
            except Exception as e:
                logger.warning(f"  ⚠️ Pattern {pid} failed on {address}: {e}")

        result.vulnerabilities = vulnerabilities
        result.scan_time_ms = (time.time() - t0) * 1000

        return result

    def _fetch_source(self, address: str) -> dict:
        """Fetch contract source code."""
        # Try cache first
        cached = get_contract_from_cache(address)
        if cached:
            return cached

        # Fetch from Etherscan
        try:
            source = fetch_contract_source(address, self.network)
            if source:
                return source
        except Exception as e:
            logger.warning(f"  ⚠️ Etherscan fetch failed for {address}: {e}")

        return {"error": "Source code not available (unverified contract or fetch failed)"}

    def _apply_pattern(
        self,
        result: ContractResult,
        pattern: dict,
        source_code: str,
        address: str,
        vulnerabilities: list,
    ):
        """Apply a single detection pattern."""
        pid = pattern.get("id", "unknown")
        pname = pattern.get("name", "Unknown Pattern")
        severity = pattern.get("severity", "medium")
        detectors = pattern.get("detectors", [])

        for detector in detectors:
            det_type = detector.get("type", "regex")
            det_pattern = detector.get("pattern", "")
            det_description = detector.get("description", "")
            det_location = detector.get("location", "")
            det_recommendation = detector.get("recommendation", "")
            det_confidence = detector.get("confidence", 0.7)

            matches = []

            if det_type == "regex":
                try:
                    flags = re.MULTILINE | re.DOTALL | re.IGNORECASE
                    for match in re.finditer(det_pattern, source_code, flags):
                        matches.append(match)
                except re.error as e:
                    logger.warning(f"  ⚠️ Bad regex in {pid}: {e}")

            elif det_type == "function_signature":
                # Look for function definitions matching criteria
                func_pattern = detector.get("func_pattern", r"function\s+\w+")
                modifier_requires = detector.get("modifier_requires", [])
                modifier_forbids = detector.get("modifier_forbids", [])

                for match in re.finditer(func_pattern, source_code, re.MULTILINE):
                    # Find the full function block
                    func_start = match.start()
                    func_block = source_code[func_start:func_start + 2000]

                    # Check modifiers
                    has_required = all(
                        m in func_block for m in modifier_requires
                    ) if modifier_requires else True
                    has_forbidden = any(
                        m in func_block for m in modifier_forbids
                    ) if modifier_forbids else False

                    if has_required and not has_forbidden:
                        matches.append(match)

            elif det_type == "ast_pattern":
                # Simplified AST-like pattern matching
                # Look for specific code structures
                required_elements = detector.get("required_elements", [])
                forbidden_elements = detector.get("forbidden_elements", [])

                all_present = all(el in source_code for el in required_elements)
                any_forbidden = any(el in source_code for el in forbidden_elements)

                if all_present and not any_forbidden:
                    # Create a virtual match
                    class VirtualMatch:
                        def groups(self):
                            return ()
                        def group(self, *args):
                            return ""
                        def start(self):
                            return 0

                    matches = [VirtualMatch()]

            for match in matches:
                # Extract snippet around the match
                start = max(0, match.start() - 100)
                end = min(len(source_code), match.end() + 200)
                snippet = source_code[start:end]

                # Truncate long snippets
                if len(snippet) > 600:
                    snippet = snippet[:300] + "\n  ...\n" + snippet[-300:]

                vuln = Vulnerability(
                    pattern_id=pid,
                    pattern_name=pname,
                    severity=severity,
                    contract=address,
                    contract_name=result.contract_name,
                    description=det_description or f"Detected {pname} pattern",
                    location=match.group() if hasattr(match, 'group') and match.groups() else det_location,
                    snippet=snippet.strip(),
                    evidence=f"Pattern matched at position {match.start()}",
                    confidence=det_confidence,
                    recommendation=det_recommendation or "Review the flagged code",
                )
                vulnerabilities.append(vuln)
