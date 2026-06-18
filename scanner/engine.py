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
    chain: str = "ethereum"       # Chain key
    chain_name: str = "Ethereum"  # Chain display name
    chain_emoji: str = "🔵"       # Chain emoji
    explorer_url: str = ""        # Link to explorer



@dataclass
class ContractResult:
    """Scan results for a single contract."""
    address: str
    contract_name: str
    compiler: str
    source_length: int
    chain: str = "ethereum"
    chain_name: str = "Ethereum"
    chain_emoji: str = "🔵"
    explorer_url: str = ""
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
    chains_scanned: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        # Build per-chain summary
        chain_summary = {}
        for addr, c in self.contracts.items():
            ch = c.chain
            if ch not in chain_summary:
                chain_summary[ch] = {
                    "chain_name": c.chain_name,
                    "chain_emoji": c.chain_emoji,
                    "contracts": 0,
                    "vulns": 0,
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                }
            chain_summary[ch]["contracts"] += 1
            chain_summary[ch]["vulns"] += c.vuln_count
            chain_summary[ch]["critical"] += c.critical_count
            chain_summary[ch]["high"] += c.high_count
            chain_summary[ch]["medium"] += c.medium_count

        return {
            "tool": "MaatEye",
            "version": "1.0.0-alpha",
            "timestamp": self.timestamp,
            "scan_time_seconds": self.scan_time_seconds,
            "total_chains": len(self.chains_scanned),
            "chains_scanned": self.chains_scanned,
            "total_contracts": self.total_contracts,
            "total_vulns": self.total_vulns,
            "critical_count": self.critical_count,
            "high_count": self.high_count,
            "medium_count": self.medium_count,
            "low_count": self.low_count,
            "chain_summary": chain_summary,
            "contracts": {
                addr: {
                    "chain": c.chain,
                    "chain_name": c.chain_name,
                    "chain_emoji": c.chain_emoji,
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
                            "chain": v.chain,
                            "chain_name": v.chain_name,
                            "description": v.description,
                            "location": v.location,
                            "snippet": v.snippet,
                            "confidence": v.confidence,
                            "recommendation": v.recommendation,
                            "explorer_url": v.explorer_url,
                        }
                        for v in c.vulnerabilities
                    ],
                }
                for addr, c in self.contracts.items()
            },
        }

    def to_markdown(self, by_chain: bool = True) -> str:
        lines = [
            "# 👁️⚖️ MaatEye Cross-Chain Scan Report\n",
            f"**Timestamp:** {self.timestamp}\n",
            f"**Chains Scanned:** {len(self.chains_scanned)}\n",
            f"**Contracts Scanned:** {self.total_contracts}\n",
            f"**Total Vulnerabilities:** {self.total_vulns}\n",
            f"**🔴 Critical:** {self.critical_count} | "
            f"**🟡 High:** {self.high_count} | "
            f"**🔵 Medium:** {self.medium_count}\n",
            "---\n",
        ]

        if by_chain and self.chains_scanned:
            # Group by chain
            chain_groups: dict[str, list[ContractResult]] = {}
            for c in self.contracts.values():
                ch = c.chain
                if ch not in chain_groups:
                    chain_groups[ch] = []
                chain_groups[ch].append(c)

            for chain_key in sorted(chain_groups.keys()):
                contracts = chain_groups[chain_key]
                c = contracts[0]
                total_v = sum(c2.vuln_count for c2 in contracts)
                crit = sum(c2.critical_count for c2 in contracts)
                high = sum(c2.high_count for c2 in contracts)
                med = sum(c2.medium_count for c2 in contracts)

                status = "🔴" if crit > 0 else ("🟡" if high > 0 else "🟢")
                lines.append(f"## {status} {c.chain_emoji} {c.chain_name} ({len(contracts)} contracts, {total_v} vulns)\n")
                
                for contract in contracts:
                    addr = contract.address
                    cs = "🔴" if contract.critical_count > 0 else ("🟡" if contract.high_count > 0 else "🟢")
                    explorer_link = f"[🔗]({contract.explorer_url}/address/{addr})" if contract.explorer_url else ""
                    lines.append(f"### {cs} `{addr[:12]}...{addr[-6:]}` {explorer_link}")
                    lines.append(f"- **Name:** {contract.contract_name or 'Unknown'}")
                    lines.append(f"- **Findings:** {contract.vuln_count} (🔴{contract.critical_count} 🟡{contract.high_count} 🔵{contract.medium_count})\n")

                    for v in contract.vulnerabilities:
                        emoji = {"critical": "🔴", "high": "🟡", "medium": "🔵", "low": "🟢"}
                        lines.append(f"  {emoji.get(v.severity, '⚪')} **{v.pattern_name}**")
                        lines.append(f"  - {v.description[:120]}")
                        lines.append(f"  - **Confidence:** {v.confidence:.0%}")
                        if v.snippet:
                            lines.append(f"  - **Snippet:** `{v.snippet[:80]}...`")
                        lines.append("")

                lines.append("---\n")
        else:
            for addr, contract in self.contracts.items():
                status = "🔴" if contract.critical_count > 0 else (
                    "🟡" if contract.high_count > 0 else (
                        "🔵" if contract.medium_count > 0 else "🟢"))
                lines.append(f"## {status} `{addr}`\n")
                lines.append(f"- **Chain:** {contract.chain_emoji} {contract.chain_name}")
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
        chain_key: Optional[str] = None,  # Multi-chain support
    ):
        self.network = network
        self.rpc_endpoint = rpc_endpoint
        self.pattern_ids = pattern_ids
        self.max_workers = max_workers
        self.chain_key = chain_key

        # Resolve chain context
        self.chain_ctx = None
        if chain_key:
            from scanner.chains import get_chain
            self.chain_ctx = get_chain(chain_key)
            if self.chain_ctx:
                self.network = chain_key

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

        logger.info(f"🧩 Loaded {len(self.active_patterns)} active patterns"
                     f"{' for ' + self.chain_ctx.name if self.chain_ctx else ''}")

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
        chain_name = self.chain_ctx.name if self.chain_ctx else "Ethereum"
        chain_key = self.chain_ctx.key if self.chain_ctx else "ethereum"
        chain_emoji = self.chain_ctx.emoji if self.chain_ctx else "🔵"
        explorer_url = self.chain_ctx.explorer_url if self.chain_ctx else ""
        logger.debug(f"  🔍 Scanning {address} on {chain_name}...")

        # Fetch source code
        source_data = self._fetch_source(address)
        if "error" in source_data:
            elapsed = (time.time() - t0) * 1000
            return ContractResult(
                address=address,
                contract_name="",
                compiler="",
                source_length=0,
                chain=chain_key,
                chain_name=chain_name,
                chain_emoji=chain_emoji,
                explorer_url=explorer_url,
                error=source_data["error"],
                scan_time_ms=elapsed,
            )

        source_code = source_data.get("source_code", "")
        contract_name = source_data.get("contract_name", "")
        compiler = source_data.get("compiler", "")
        source_chain = source_data.get("chain", chain_key)

        result = ContractResult(
            address=address,
            contract_name=contract_name,
            compiler=compiler,
            source_length=len(source_code),
            chain=source_chain,
            chain_name=source_data.get("chain_name", chain_name),
            chain_emoji=chain_emoji,
            explorer_url=explorer_url,
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
        """Fetch contract source code from the appropriate chain."""
        # Try cache first
        cached = get_contract_from_cache(address)
        if cached:
            return cached

        # If chain context is set, use multi-chain fetcher
        if self.chain_ctx:
            from scanner.fetchers.multichain import fetch_contract_source as mc_fetch
            try:
                source = mc_fetch(address, self.chain_ctx)
                if source:
                    return source
            except Exception as e:
                logger.warning(f"  ⚠️ Multi-chain fetch failed for {address}: {e}")
        else:
            # Legacy: try Etherscan (Ethereum mainnet)
            try:
                source = fetch_contract_source(address, self.network)
                if source:
                    return source
            except Exception as e:
                logger.warning(f"  ⚠️ Etherscan fetch failed for {address}: {e}")

        return {"error": "Source code not available (unverified contract or fetch failed)"}

    def scan_chain(self, chain_key: str, count: int = 20) -> ScanResults:
        """
        Discover and scan top tokens on a specific chain.
        Harmless: READ-ONLY — never sends transactions, never exploits.
        """
        from scanner.chains import get_chain, EVM_CHAINS
        from scanner.fetchers.token_discovery import discover_top_tokens

        chain = get_chain(chain_key)
        if not chain:
            logger.error(f"❌ Unknown chain: {chain_key}")
            return ScanResults(timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

        logger.info(f"🌐 Scanning {chain.emoji} {chain.name}...")

        # Discover tokens
        addresses = discover_top_tokens(chain, count=count)
        if not addresses:
            logger.warning(f"  ⚠️ No tokens found on {chain.name}")
            return ScanResults(timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

        # Create chain-specific engine
        chain_engine = ScanEngine(
            chain_key=chain_key,
            pattern_ids=self.pattern_ids,
            max_workers=min(self.max_workers, 3),  # Be gentle with explorer APIs
        )

        # Scan
        results = chain_engine.scan(addresses)
        return results

    def scan_all_chains(self, tokens_per_chain: int = 10) -> ScanResults:
        """
        Scan top tokens across ALL EVM chains.
        Generates a cross-chain vulnerability report.
        Harmless: READ-ONLY — purely static analysis.
        """
        from scanner.chains import list_chains
        from scanner.fetchers.token_discovery import discover_all_chains

        chains = list_chains()
        all_addresses: dict[str, list[str]] = {}
        total_expected = 0

        logger.info(f"🌍 Cross-chain scan: {len(chains)} chains")

        # Discover tokens on all chains
        for chain in chains:
            try:
                from scanner.fetchers.token_discovery import discover_top_tokens
                addrs = discover_top_tokens(chain, count=tokens_per_chain)
                if addrs:
                    all_addresses[chain.key] = addrs
                    total_expected += len(addrs)
            except Exception as e:
                logger.warning(f"  ⚠️ Token discovery failed for {chain.name}: {e}")

        # Scan each chain
        start_time = time.time()
        master_results = ScanResults(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

        for chain_key, addresses in all_addresses.items():
            chain_engine = ScanEngine(
                chain_key=chain_key,
                pattern_ids=self.pattern_ids,
                max_workers=min(self.max_workers, 3),
            )
            chain_results = chain_engine.scan(addresses)
            master_results.contracts.update(chain_results.contracts)

        # Aggregate
        master_results.total_contracts = len(master_results.contracts)
        master_results.chains_scanned = list(all_addresses.keys())
        master_results.scan_time_seconds = round(time.time() - start_time, 2)

        for c in master_results.contracts.values():
            master_results.total_vulns += c.vuln_count
            master_results.critical_count += c.critical_count
            master_results.high_count += c.high_count
            master_results.medium_count += c.medium_count

        logger.info(f"✅ Cross-chain scan complete: "
                     f"{len(master_results.chains_scanned)} chains, "
                     f"{master_results.total_contracts} contracts, "
                     f"{master_results.total_vulns} vulns")

        return master_results

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
