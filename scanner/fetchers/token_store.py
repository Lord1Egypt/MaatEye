"""
🗄️ MaatEye — Persistent Token Store
Deduplicated, incremental token storage with JSON backend.
Tracks which tokens have been scanned, when, and what was found.
"""

import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

from scanner.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_STORAGE_DIR = Path(__file__).parent.parent.parent / "data"


@dataclass
class StoredToken:
    """A token entry in the persistent store."""
    address: str
    chain: str
    symbol: str = ""
    name: str = ""
    decimals: int = 18
    source: str = "unknown"
    discovered_at: float = 0.0
    discovered_at_block: int = 0
    last_scanned: float = 0.0
    scan_count: int = 0
    has_source: bool = False
    verified_source: bool = False  # True only when real verified Solidity was analyzed
    vuln_count: int = 0
    max_severity: str = ""
    latest_result_hash: str = ""


class TokenStore:
    """
    Persistent, deduplicated token store.
    
    Features:
    - JSON-based (zero external dependencies)
    - Deduplication by (chain, address)
    - Tracks new vs already-seen tokens
    - Incremental updates only
    - Scan history tracking
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or DEFAULT_STORAGE_DIR
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.json_path = self.storage_path / "token_registry.json"
        self.tokens: dict[str, dict[str, StoredToken]] = {}
        self._dirty = False
        
        self._load()
    
    def _load(self):
        """Load token registry from disk."""
        if self.json_path.exists():
            try:
                raw = json.loads(self.json_path.read_text())
                for chain, chain_tokens in raw.items():
                    if chain not in self.tokens:
                        self.tokens[chain] = {}
                    for addr, data in chain_tokens.items():
                        self.tokens[chain][addr.lower()] = StoredToken(**data)
                total = sum(len(t) for t in self.tokens.values())
                logger.info(f"🗄️  Loaded {total} tokens from registry ({len(self.tokens)} chains)")
            except Exception as e:
                logger.warning(f"⚠️  Failed to load token registry: {e}")
                self.tokens = {}
        else:
            logger.info("🗄️  No existing token registry — starting fresh")
            self.tokens = {}
    
    def save(self):
        """Persist token registry to disk."""
        raw = {}
        for chain, chain_tokens in self.tokens.items():
            raw[chain] = {addr: asdict(t) for addr, t in chain_tokens.items()}
        self.json_path.write_text(json.dumps(raw, indent=2, default=str))
        total = sum(len(t) for t in self.tokens.values())
        logger.info(f"💾 Saved {total} tokens to registry ({len(self.tokens)} chains)")
        self._dirty = False
    
    def add_tokens(self, tokens: list[StoredToken]) -> dict:
        """
        Add tokens, skipping duplicates. Returns stats.
        
        Returns:
            dict with keys: added (int), skipped_duplicates (int), total (int)
        """
        added = 0
        skipped = 0
        
        for token in tokens:
            addr = token.address.lower()
            chain = token.chain
            
            if chain not in self.tokens:
                self.tokens[chain] = {}
            
            if addr in self.tokens[chain]:
                skipped += 1
                existing = self.tokens[chain][addr]
                if token.symbol and not existing.symbol:
                    existing.symbol = token.symbol
                if token.name and not existing.name:
                    existing.name = token.name
                if token.decimals != 18 and existing.decimals == 18:
                    existing.decimals = token.decimals
            else:
                token.address = addr
                if not token.discovered_at:
                    token.discovered_at = time.time()
                self.tokens[chain][addr] = token
                added += 1
        
        if added > 0:
            self._dirty = True
            self.save()
        
        total = sum(len(t) for t in self.tokens.values())
        return {"added": added, "skipped_duplicates": skipped, "total": total}
    
    def get_new_tokens_since(self, timestamp: float) -> list[StoredToken]:
        """Get tokens discovered since a given timestamp."""
        new_tokens = []
        for chain_tokens in self.tokens.values():
            for token in chain_tokens.values():
                if token.discovered_at > timestamp:
                    new_tokens.append(token)
        return new_tokens
    
    def get_unscanned_tokens(self) -> list[StoredToken]:
        """Get tokens that have never been scanned."""
        unscanned = []
        for chain_tokens in self.tokens.values():
            for token in chain_tokens.values():
                if token.scan_count == 0:
                    unscanned.append(token)
        return unscanned
    
    def get_tokens_by_chain(self, chain: str) -> list[StoredToken]:
        """Get all tokens for a specific chain."""
        return list(self.tokens.get(chain, {}).values())
    
    def get_all_tokens(self) -> list[StoredToken]:
        """Get all tokens across all chains."""
        all_tokens = []
        for chain_tokens in self.tokens.values():
            all_tokens.extend(chain_tokens.values())
        return all_tokens
    
    def get_chain_stats(self) -> dict:
        """Get per-chain token statistics."""
        stats = {}
        for chain, chain_tokens in self.tokens.items():
            with_source = sum(1 for t in chain_tokens.values() if t.has_source)
            analyzed = sum(1 for t in chain_tokens.values()
                           if t.verified_source or t.vuln_count > 0)
            with_vulns = sum(1 for t in chain_tokens.values() if t.vuln_count > 0)
            stats[chain] = {
                "total": len(chain_tokens),
                "with_source": with_source,
                "analyzed": analyzed,
                "with_vulns": with_vulns,
                "unscanned": sum(1 for t in chain_tokens.values() if t.scan_count == 0),
                "critical": sum(1 for t in chain_tokens.values() if t.max_severity == "critical"),
                "high": sum(1 for t in chain_tokens.values() if t.max_severity == "high"),
            }
        return stats
    
    def update_scan_result(self, chain: str, address: str,
                           vuln_count: int, max_severity: str,
                           result_hash: str = ""):
        """Update scan result for a token."""
        addr = address.lower()
        if chain in self.tokens and addr in self.tokens[chain]:
            token = self.tokens[chain][addr]
            token.last_scanned = time.time()
            token.scan_count += 1
            token.vuln_count = vuln_count
            token.max_severity = max_severity
            if result_hash:
                token.latest_result_hash = result_hash
            self._dirty = True
    
    def mark_has_source(self, chain: str, address: str, verified: bool = False):
        """
        Mark a token as having fetched source.

        `verified=True` means real verified Solidity was retrieved and analyzed.
        `verified=False` covers bytecode-only placeholders (contract exists but the
        source was never verified) — these must NOT count as real coverage.
        """
        addr = address.lower()
        if chain in self.tokens and addr in self.tokens[chain]:
            self.tokens[chain][addr].has_source = True
            if verified:
                self.tokens[chain][addr].verified_source = True
            self._dirty = True
    
    def apply_scan_results(self, scan_results, source: str = "scan") -> int:
        """Persist a ScanResults object back into the registry (upsert).

        For every successfully-scanned contract this records vuln_count,
        max_severity, and — only when *real* verified Solidity was analyzed
        (``has_verified_source``) — credits it as verified coverage. Tokens not
        yet in the registry are inserted so freshly-scanned top tokens show up
        on the dashboard. Returns the number of contracts applied.

        Duck-typed against ``scanner.engine`` result objects to avoid a circular
        import. Caller is responsible for ``save()``.
        """
        applied = 0
        contracts = getattr(scan_results, "contracts", {}) or {}
        for addr, c in contracts.items():
            if getattr(c, "error", None):
                continue
            chain = getattr(c, "chain", "") or ""
            if not chain:
                continue
            key = addr.lower()

            if c.critical_count > 0:
                max_sev = "critical"
            elif c.high_count > 0:
                max_sev = "high"
            elif c.medium_count > 0:
                max_sev = "medium"
            elif c.vuln_count > 0:
                max_sev = "low"
            else:
                max_sev = ""

            self.tokens.setdefault(chain, {})
            tok = self.tokens[chain].get(key)
            if tok is None:
                tok = StoredToken(
                    address=key, chain=chain,
                    symbol=getattr(c, "contract_name", "") or "",
                    source=source, discovered_at=time.time(),
                )
                self.tokens[chain][key] = tok

            tok.last_scanned = time.time()
            tok.scan_count += 1
            tok.vuln_count = c.vuln_count
            tok.max_severity = max_sev
            # Only real verified source counts as "analyzed"; a bytecode-only
            # placeholder (source_length 0 / unverified) must not inflate it.
            if getattr(c, "source_length", 0) > 0:
                tok.has_source = True
                if getattr(c, "has_verified_source", False):
                    tok.verified_source = True
            applied += 1

        if applied:
            self._dirty = True
        return applied

    def get_summary(self) -> str:
        """Get a human-readable summary of the registry."""
        stats = self.get_chain_stats()
        total = sum(s["total"] for s in stats.values())
        total_unscanned = sum(s["unscanned"] for s in stats.values())
        lines = [
            "📊  TOKEN REGISTRY SUMMARY",
            "=" * 50,
            f"  Total tokens: {total}",
            f"  Total chains: {len(stats)}",
            f"  Unscanned:    {total_unscanned}",
            "",
        ]
        for chain, s in sorted(stats.items()):
            lines.append(
                f"  {chain:<12} {s['total']:>6} tokens  "
                f"(source: {s['with_source']}, "
                f"new: {s['unscanned']}, "
                f"vulns: {s['with_vulns']})"
            )
        return "\n".join(lines)


# Global singleton
_store: Optional[TokenStore] = None


def get_store() -> TokenStore:
    """Get or create the global token store singleton."""
    global _store
    if _store is None:
        _store = TokenStore()
    return _store


def bulk_add_from_discovery(
    chain: str,
    addresses: set[str],
    source: str = "rpc_event_log",
    block: int = 0,
) -> dict:
    """Convenience: bulk-add discovered addresses to the store."""
    store = get_store()
    now = time.time()
    tokens = [StoredToken(address=a, chain=chain, source=source,
                          discovered_at=now, discovered_at_block=block)
              for a in sorted(addresses)]
    return store.add_tokens(tokens)


if __name__ == "__main__":
    store = get_store()
    print(store.get_summary())
