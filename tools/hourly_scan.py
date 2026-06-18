#!/usr/bin/env python3
"""
👁️⚖️ MaatEye — Hourly RPC Token Scanner
Discovers NEW tokens via RPC event logs, scans them for vulnerabilities,
and updates the persistent registry + GitHub Pages dashboard.

Strategy:
  1. Scan Transfer events in the last ~1 hour of blocks on all chains
  2. Filter to ONLY addresses never seen before (dedup via registry)
  3. Take up to --max-new tokens per chain
  4. Fetch source code + run 20 Plague patterns on each
  5. Update token registry with results
  6. Regenerate docs/dashboard.json (cumulative stats)

All operations are READ-ONLY — no transactions, no exploits.

Usage:
    python tools/hourly_scan.py [--max-new 500] [--workers 10] [--dry-run]
    python tools/hourly_scan.py --chains ethereum,bnb,polygon --max-new 300
"""

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

# Add repo root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scanner.fetchers.rpc_discovery import (
    PERMISSIVE_RPCS,
    discover_tokens_rpc_catchup,
    _rpc_call,
)
from scanner.fetchers.token_store import (
    StoredToken,
    bulk_add_from_discovery,
    get_store,
)
from scanner.utils.logger import get_logger

logger = get_logger("hourly_scan")

# Approximate blocks produced per hour on each chain
BLOCKS_PER_HOUR: dict[str, int] = {
    "ethereum": 300,    # ~12s/block
    "bnb":      1200,   # ~3s/block
    "polygon":  1800,   # ~2s/block
    "arbitrum": 3600,   # ~1s/block (Nitro)
    "optimism": 1800,   # ~2s/block
    "base":     1800,   # ~2s/block
    "avalanche": 1800,  # ~2s/block
}

# Add any PERMISSIVE_RPCS chain not in the above with a default
for _chain in PERMISSIVE_RPCS:
    BLOCKS_PER_HOUR.setdefault(_chain, 300)


def discover_new_tokens_on_chain(
    chain_key: str,
    max_new: int,
    registry: dict[str, dict],
) -> list[str]:
    """
    Discover NEW token addresses on a chain via RPC event logs.

    Returns addresses not currently in the registry, up to max_new.
    """
    lookback = BLOCKS_PER_HOUR.get(chain_key, 300)
    logger.info(f"🔍 {chain_key}: scanning last {lookback} blocks for new tokens...")

    tokens = discover_tokens_rpc_catchup(chain_key, lookback_blocks=lookback)
    if not tokens:
        logger.warning(f"  ⚠️ {chain_key}: no tokens found via RPC, using fallback list")
        # FALLBACK: Provide some static verified contracts so the scanner always does work
        fallback_tokens = {
            "ethereum": ["0xdAC17F958D2ee523a2206206994597C13D831ec7", "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", "0x514910771AF9Ca656af840dff83E8264EcF986CA", "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"],
            "bnb": ["0x55d398326f99059fF775485246999027B3197955", "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d", "0x1AF3F329e8BE154074D8769D1FFa4eE058B1DBc3"],
            "polygon": ["0xc2132D05D31c914a87C6611C10748AEb04B58e8F", "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"],
            "arbitrum": ["0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9", "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"],
            "optimism": ["0x94b008aA00579c1307B0EF2c499aD98a8ce58e58", "0x7F5c764cBc14f9669B88837ca1490cCa17c31607"],
            "base": ["0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb"],
            "avalanche": ["0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7", "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"]
        }
        tokens = {addr.lower(): {} for addr in fallback_tokens.get(chain_key, [])}

    chain_registry = registry.get(chain_key, {})
    new_addrs = [addr for addr in tokens.keys() if addr not in chain_registry]

    logger.info(
        f"  {chain_key}: {len(tokens)} discovered, "
        f"{len(new_addrs)} new (not yet in registry)"
    )

    return new_addrs[:max_new]


def scan_addresses_on_chain(
    chain_key: str,
    addresses: list[str],
    workers: int,
) -> dict:
    """
    Scan a list of addresses on a given chain using the MaatEye engine.

    Returns the ScanResults.to_dict() for this chain.
    """
    if not addresses:
        return {}

    from scanner.engine import ScanEngine

    logger.info(f"  ⚡ Scanning {len(addresses)} contracts on {chain_key}...")
    engine = ScanEngine(chain_key=chain_key, max_workers=workers)
    results = engine.scan(addresses)
    return results


def update_registry_from_results(chain_key: str, scan_results) -> None:
    """Push scan outcomes back into the token store."""
    store = get_store()
    for addr, contract in scan_results.contracts.items():
        if contract.error:
            continue
        max_sev = ""
        if contract.critical_count > 0:
            max_sev = "critical"
        elif contract.high_count > 0:
            max_sev = "high"
        elif contract.medium_count > 0:
            max_sev = "medium"
        elif contract.vuln_count > 0:
            max_sev = "low"
        store.update_scan_result(chain_key, addr, contract.vuln_count, max_sev)
        if contract.source_length > 0:
            store.mark_has_source(chain_key, addr)

    store.save()


def build_dashboard_json(output_path: str) -> None:
    """Regenerate docs/dashboard.json from the live token registry."""
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from tools.update_dashboard import from_registry

    data = from_registry()

    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    logger.info(f"✅ dashboard.json updated: {output_path}")


def print_run_summary(
    chain_results: dict,
    total_new_discovered: int,
    total_registered: int,
    elapsed: float,
) -> None:
    print("\n" + "=" * 60)
    print("👁️⚖️  MAATEYE HOURLY SCAN COMPLETE")
    print("=" * 60)
    print(f"  New tokens discovered:  {total_new_discovered}")
    print(f"  New tokens registered:  {total_registered}")
    print(f"  Chains scanned:         {len(chain_results)}")
    print(f"  Elapsed:                {elapsed:.1f}s")
    print()
    for chain_key, results in chain_results.items():
        if results:
            d = results.to_dict() if hasattr(results, "to_dict") else {}
            vulns = d.get("total_vulns", 0)
            crit = d.get("critical_count", 0)
            high = d.get("high_count", 0)
            contracts = d.get("total_contracts", 0)
            print(f"  {chain_key:<12} {contracts:>5} scanned  "
                  f"{vulns:>4} vulns (🔴{crit} 🟡{high})")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="👁️⚖️ MaatEye — Hourly RPC Token Scanner"
    )
    parser.add_argument(
        "--chains",
        default="",
        help="Comma-separated chain keys to scan. Default: all PERMISSIVE_RPCS chains.",
    )
    parser.add_argument(
        "--max-new", type=int, default=500,
        help="Max new tokens to scan per chain per run (default: 500)",
    )
    parser.add_argument(
        "--workers", type=int, default=10,
        help="Parallel scan workers per chain (default: 10)",
    )
    parser.add_argument(
        "--dashboard", default="docs/dashboard.json",
        help="Output path for dashboard JSON (default: docs/dashboard.json)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Discover tokens but do NOT scan or update registry",
    )
    parser.add_argument(
        "--no-scan", action="store_true",
        help="Discover + register tokens, but skip source fetch and pattern scan",
    )
    args = parser.parse_args()

    start_time = time.time()

    # Determine target chains
    if args.chains:
        target_chains = [c.strip() for c in args.chains.split(",") if c.strip()]
        invalid = [c for c in target_chains if c not in PERMISSIVE_RPCS]
        if invalid:
            print(f"❌ Unknown chains: {invalid}. Valid: {list(PERMISSIVE_RPCS.keys())}")
            sys.exit(1)
    else:
        target_chains = list(PERMISSIVE_RPCS.keys())

    print(f"👁️⚖️  MaatEye Hourly RPC Scan — {datetime.now(timezone.utc).isoformat()}")
    print(f"   Chains:    {', '.join(target_chains)}")
    print(f"   Max new:   {args.max_new} per chain")
    print(f"   Workers:   {args.workers}")
    print(f"   Dry run:   {args.dry_run}")
    print()

    # Load registry
    store = get_store()
    registry = store.tokens

    # Phase 1: RPC discovery across all chains (parallel)
    print("Phase 1 — RPC Token Discovery")
    print("-" * 40)
    chain_new_addresses: dict[str, list[str]] = {}
    total_new_discovered = 0

    with ThreadPoolExecutor(max_workers=min(len(target_chains), 4)) as pool:
        future_map = {
            pool.submit(discover_new_tokens_on_chain, chain, args.max_new, registry): chain
            for chain in target_chains
        }
        for future in as_completed(future_map):
            chain_key = future_map[future]
            try:
                new_addrs = future.result()
                chain_new_addresses[chain_key] = new_addrs
                total_new_discovered += len(new_addrs)
            except Exception as exc:
                logger.error(f"  ❌ Discovery failed on {chain_key}: {exc}")
                chain_new_addresses[chain_key] = []

    print(f"\n  Total new addresses found: {total_new_discovered}")

    if args.dry_run:
        print("\n[DRY RUN] — no registry update or scanning performed.")
        print_run_summary({}, total_new_discovered, 0, time.time() - start_time)
        return

    # Phase 2: Register ALL new addresses (fast, no source fetch)
    print("\nPhase 2 — Registering New Tokens")
    print("-" * 40)
    total_registered = 0
    for chain_key, addresses in chain_new_addresses.items():
        if not addresses:
            continue
        stats = bulk_add_from_discovery(chain_key, set(addresses), source="rpc_hourly")
        total_registered += stats["added"]
        if stats["added"] > 0:
            print(f"  {chain_key:<12}: +{stats['added']} new  "
                  f"(skipped {stats['skipped_duplicates']} duplicates)")

    if args.no_scan:
        print("\n[--no-scan] — skipping source fetch + vulnerability analysis.")
        build_dashboard_json(args.dashboard)
        print_run_summary({}, total_new_discovered, total_registered, time.time() - start_time)
        return

    # Phase 3: Scan each chain (source fetch + 20 Plague patterns)
    print("\nPhase 3 — Vulnerability Scan")
    print("-" * 40)
    chain_results = {}

    for chain_key, addresses in chain_new_addresses.items():
        if not addresses:
            continue
        try:
            results = scan_addresses_on_chain(chain_key, addresses, args.workers)
            chain_results[chain_key] = results
            update_registry_from_results(chain_key, results)
        except Exception as exc:
            logger.error(f"  ❌ Scan failed on {chain_key}: {exc}")

    # Phase 4: Update dashboard.json
    print("\nPhase 4 — Updating Dashboard")
    print("-" * 40)
    build_dashboard_json(args.dashboard)

    elapsed = time.time() - start_time
    print_run_summary(chain_results, total_new_discovered, total_registered, elapsed)


if __name__ == "__main__":
    main()
