"""
MaatEye — Main Entry Point

Usage:
    python -m scanner.main scan --address 0x...
    python -m scanner.main scan --top 20
    python -m scanner.main patterns list
    python -m scanner.main validate --all-patterns
"""

import argparse
import json
import sys
from pathlib import Path

from scanner.utils.config import load_config, get_all_patterns
from scanner.utils.logger import get_logger

logger = get_logger(__name__)


def _write_output(path: str, content: str) -> None:
    """Write text to ``path``, creating parent directories as needed.

    Output targets like ``results/cross_chain_report.json`` live in a directory
    that may not exist yet (e.g. fresh CI checkout), so ensure it first.
    """
    p = Path(path)
    if p.parent and not p.parent.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


def main():
    parser = argparse.ArgumentParser(
        prog="maateye",
        description="👁️⚖️ MaatEye — Smart Contract Vulnerability Scanner",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ── Scan Command ────────────────────────────────────────────────────────
    scan_parser = subparsers.add_parser("scan", help="Scan contracts for vulnerabilities")
    scan_parser.add_argument("--address", help="Single contract address to scan")
    scan_parser.add_argument("--addresses", help="Comma-separated contract addresses")
    scan_parser.add_argument("--file", help="File with contract addresses (one per line)")
    scan_parser.add_argument("--top", type=int, default=0,
                             help="Scan top N tokens by market cap (auto-fetch)")
    scan_parser.add_argument("--patterns", default="all",
                             help="Comma-separated pattern IDs or 'all'")
    scan_parser.add_argument("--format", choices=["json", "markdown", "text"],
                             default="json", help="Output format")
    scan_parser.add_argument("--output", help="Output file path")
    scan_parser.add_argument("--network", default="mainnet",
                             help="Ethereum network (mainnet, sepolia, etc.)")
    scan_parser.add_argument("--rpc", help="Custom RPC endpoint")
    scan_parser.add_argument("--chain", default=None,
                             help="Chain to scan (ethereum, bnb, polygon, etc.)")

    # ── Scan-Chain Command ──────────────────────────────────────────────────
    chain_parser = subparsers.add_parser("scan-chain",
        help="Scan top tokens on a specific chain")
    chain_parser.add_argument("chain", help="Chain key (ethereum, bnb, polygon, etc.)")
    chain_parser.add_argument("--count", type=int, default=10,
                              help="Number of top tokens to scan")
    chain_parser.add_argument("--patterns", default="all",
                              help="Comma-separated pattern IDs or 'all'")
    chain_parser.add_argument("--format", choices=["json", "markdown", "text"],
                              default="json", help="Output format")
    chain_parser.add_argument("--output", help="Output file path")

    # ── Scan-All Command ────────────────────────────────────────────────────
    scan_all_parser = subparsers.add_parser("scan-all",
        help="Scan top tokens across ALL supported EVM chains")
    scan_all_parser.add_argument("--tokens-per-chain", type=int, default=10,
                                 help="Number of top tokens per chain")
    scan_all_parser.add_argument("--patterns", default="all",
                                 help="Comma-separated pattern IDs or 'all'")
    scan_all_parser.add_argument("--format", choices=["json", "markdown", "text"],
                                 default="json", help="Output format")
    scan_all_parser.add_argument("--output", help="Output file path")

    # ── Chains Command ──────────────────────────────────────────────────────
    chains_parser = subparsers.add_parser("chains", help="List supported chains")
    chains_parser.add_argument("--show-all", action="store_true",
                               help="Show all chains including RPC URLs")

    # ── Patterns Command ────────────────────────────────────────────────────
    patterns_parser = subparsers.add_parser("patterns", help="Manage detection patterns")
    patterns_parser.add_argument("action", choices=["list", "show", "add", "remove"],
                                 help="Pattern action")
    patterns_parser.add_argument("pattern_id", nargs="?", help="Pattern ID")

    # ── Validate Command ────────────────────────────────────────────────────
    validate_parser = subparsers.add_parser("validate", help="Validate patterns/tests")
    validate_parser.add_argument("--pattern", help="Specific pattern to validate")
    validate_parser.add_argument("--all-patterns", action="store_true",
                                 help="Validate all patterns")
    validate_parser.add_argument("--contract", help="Validate against a real contract")

    # ── Reindex Command ─────────────────────────────────────────────────────
    reindex_parser = subparsers.add_parser("reindex", help="Re-index pattern registry")

    # ── Tokens Command ──────────────────────────────────────────────────────
    tokens_parser = subparsers.add_parser("tokens", help="Manage discovered token registry")
    tokens_sub = tokens_parser.add_subparsers(dest="tokens_action", help="Token action")

    # tokens import
    tokens_import = tokens_sub.add_parser("import", help="Import tokens from discovery sources")
    tokens_import.add_argument("--sources", default="coingecko,explorer,known",
                               help="Comma-separated sources (coingecko,explorer,known,rpc)")
    tokens_import.add_argument("--rpc-blocks", type=int, default=20000,
                               help="Lookback blocks for RPC discovery")
    tokens_import.add_argument("--explorer-count", type=int, default=50,
                               help="Tokens per chain from explorer API")
    tokens_import.add_argument("--save", action="store_true", default=True,
                               help="Save to token registry (default: True)")

    # tokens stats
    tokens_sub.add_parser("stats", help="Show token registry statistics")

    # tokens new
    tokens_new = tokens_sub.add_parser("new", help="Show newly discovered tokens")
    tokens_new.add_argument("--since", type=float, default=0,
                            help="Unix timestamp (0 = last session)")

    # tokens export
    tokens_export = tokens_sub.add_parser("export", help="Export token addresses")
    tokens_export.add_argument("--chain", help="Filter by chain key")
    tokens_export.add_argument("--format", choices=["txt", "json", "csv"], default="txt")
    tokens_export.add_argument("--output", help="Output file path")

    # tokens list
    tokens_list = tokens_sub.add_parser("list", help="List tokens for a chain")
    tokens_list.add_argument("chain", help="Chain key (ethereum, bnb, polygon, etc.)")
    tokens_list.add_argument("--limit", type=int, default=50, help="Max tokens to show")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "scan":
        run_scan(args)
    elif args.command == "scan-chain":
        run_scan_chain(args)
    elif args.command == "scan-all":
        run_scan_all(args)
    elif args.command == "chains":
        run_chains(args)
    elif args.command == "patterns":
        manage_patterns(args)
    elif args.command == "validate":
        run_validate(args)
    elif args.command == "reindex":
        run_reindex(args)
    elif args.command == "tokens":
        run_tokens(args)


def run_tokens(args):
    """Handle token management commands."""
    from scanner.fetchers.token_store import get_store

    if not args.tokens_action:
        print("Usage: python -m scanner.main tokens [import|stats|new|export|list]")
        print("Run: python -m scanner.main tokens --help")
        return

    action = args.tokens_action

    # ── tokens stats ────────────────────────────────────────────────────
    if action == "stats":
        store = get_store()
        print(store.get_summary())
        return

    # ── tokens import ───────────────────────────────────────────────────
    if action == "import":
        from scanner.fetchers.token_discovery import discover_all_tokens
        from scanner.fetchers.token_store import bulk_add_from_discovery

        sources = [s.strip() for s in args.sources.split(",")]

        print("🔍 Token Discovery Import")
        print("=" * 50)

        # Run discovery
        result = discover_all_tokens(
            use_coingecko="coingecko" in sources,
            use_rpc="rpc" in sources,
            use_explorer="explorer" in sources,
            use_known="known" in sources,
            tokens_per_chain_explorer=args.explorer_count,
        )

        total = sum(len(v) for v in result.values())
        print(f"\n📦 Discovered {total} unique token addresses across {len(result)} chains")

        # Import into store
        if args.save:
            store = get_store()
            import time
            grand_added = 0
            grand_skipped = 0
            for chain, addresses in sorted(result.items()):
                stats = bulk_add_from_discovery(
                    chain=chain,
                    addresses=addresses,
                    source="discovery_import",
                    block=0,
                )
                grand_added += stats["added"]
                grand_skipped += stats["skipped_duplicates"]

            print(f"\n💾 Registry updated:")
            print(f"   ✅ {grand_added} new tokens added")
            print(f"   ⏭️  {grand_skipped} duplicates skipped")
            print(f"   📊 Total in registry: {stats['total']}")
        return

    # ── tokens new ──────────────────────────────────────────────────────
    if action == "new":
        store = get_store()
        new_tokens = store.get_new_tokens_since(args.since)
        if not new_tokens:
            print("✨ No new tokens found")
            return

        print(f"🆕 {len(new_tokens)} new tokens since timestamp {args.since}")
        print("-" * 60)
        for t in new_tokens:
            src = t.source[:12]
            print(f"  {t.chain:<12} {t.address:<42} [{src}]")
        return

    # ── tokens export ───────────────────────────────────────────────────
    if action == "export":
        store = get_store()
        if args.chain:
            tokens = store.get_tokens_by_chain(args.chain)
            label = args.chain
        else:
            tokens = store.get_all_tokens()
            label = "all_chains"

        if args.format == "json":
            data = {t.chain: t.address for t in tokens}
            content = json.dumps(data, indent=2)
            ext = "json"
        elif args.format == "csv":
            lines = ["chain,address,symbol,name,source"]
            for t in tokens:
                lines.append(f"{t.chain},{t.address},{t.symbol},{t.name},{t.source}")
            content = "\n".join(lines)
            ext = "csv"
        else:
            content = "\n".join(sorted(set(t.address for t in tokens)))
            ext = "txt"

        output_path = args.output or f"data/token_export_{label}.{ext}"
        _write_output(output_path, content)
        print(f"📤 Exported {len(tokens)} tokens → {output_path}")
        return

    # ── tokens list ─────────────────────────────────────────────────────
    if action == "list":
        store = get_store()
        tokens = store.get_tokens_by_chain(args.chain)
        if not tokens:
            print(f"❌ No tokens found for chain '{args.chain}'")
            print(f"   Available chains: {', '.join(sorted(store.tokens.keys()))}")
            return

        print(f"\n📋 Tokens on {args.chain} ({len(tokens)} total)")
        print("=" * 60)
        limit = min(args.limit, len(tokens))
        for t in sorted(tokens, key=lambda x: x.discovered_at, reverse=True)[:limit]:
            src = t.source[:10]
            scanned = "✅" if t.scan_count > 0 else "⬜"
            sev = f" [{t.max_severity}]" if t.max_severity else ""
            print(f"  {scanned} {t.address}  {t.symbol:<8} [{src}]{sev}")

        if limit < len(tokens):
            print(f"\n   ... and {len(tokens) - limit} more (use --limit to show more)")
        return


def collect_addresses(args) -> list[str]:
    """Collect contract addresses from all input sources."""
    addresses = set()

    if args.address:
        addresses.add(args.address.strip().lower())

    if args.addresses:
        for addr in args.addresses.split(","):
            addresses.add(addr.strip().lower())

    if args.file:
        with open(args.file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    addresses.add(line.lower())

    if args.top:
        logger.info(f"🌐 Fetching top {args.top} token addresses...")
        try:
            from scanner.fetchers.coingecko import fetch_top_tokens
            top_addrs = fetch_top_tokens(args.top)
            addresses.update(top_addrs)
        except ImportError:
            logger.warning("Coingecko fetcher not available, using default list")
            from scanner.fetchers.default import get_default_tokens
            addresses.update(get_default_tokens(args.top))

    return list(addresses)


def run_scan(args):
    """Execute the vulnerability scan."""
    from scanner.engine import ScanEngine

    addresses = collect_addresses(args)
    if not addresses:
        logger.error("❌ No contract addresses provided")
        sys.exit(1)

    logger.info(f"🔍 Scanning {len(addresses)} contract(s)...")

    pattern_ids = None
    if args.patterns and args.patterns != "all":
        pattern_ids = [p.strip() for p in args.patterns.split(",")]

    engine = ScanEngine(
        network=args.network,
        rpc_endpoint=args.rpc,
        pattern_ids=pattern_ids,
        chain_key=args.chain,
    )

    results = engine.scan(addresses)

    # Format output
    if args.format == "json":
        output = json.dumps(results.to_dict(), indent=2)
    elif args.format == "markdown":
        output = results.to_markdown()
    else:
        output = results.to_text()

    if args.output:
        _write_output(args.output, output)
        logger.info(f"✅ Results written to {args.output}")
    else:
        print(output)


def run_scan_chain(args):
    """Scan top tokens on a specific chain."""
    from scanner.engine import ScanEngine

    logger.info(f"🌐 Scanning chain: {args.chain}")

    pattern_ids = None
    if args.patterns and args.patterns != "all":
        pattern_ids = [p.strip() for p in args.patterns.split(",")]

    engine = ScanEngine(
        pattern_ids=pattern_ids,
        chain_key=args.chain,
    )

    results = engine.scan_chain(args.chain, count=args.count)

    # Format output
    if args.format == "json":
        output = json.dumps(results.to_dict(), indent=2)
    elif args.format == "markdown":
        output = results.to_markdown()
    else:
        output = results.to_text()

    if args.output:
        _write_output(args.output, output)
        logger.info(f"✅ Results written to {args.output}")
    else:
        print(output)


def run_scan_all(args):
    """Scan top tokens across ALL supported EVM chains."""
    from scanner.engine import ScanEngine

    logger.info("🌍 Cross-chain scan — ALL EVM chains")

    pattern_ids = None
    if args.patterns and args.patterns != "all":
        pattern_ids = [p.strip() for p in args.patterns.split(",")]

    engine = ScanEngine(pattern_ids=pattern_ids)

    results = engine.scan_all_chains(tokens_per_chain=args.tokens_per_chain)

    # Format output
    if args.format == "json":
        output = json.dumps(results.to_dict(), indent=2)
    elif args.format == "markdown":
        output = results.to_markdown()
    else:
        output = results.to_text()

    if args.output:
        _write_output(args.output, output)
        logger.info(f"✅ Cross-chain results written to {args.output}")
    else:
        print(output)


def run_chains(args):
    """List all supported EVM chains."""
    from scanner.chains import EVM_CHAINS, ALIASES

    print("\n🌐 🌐 🌐  MAATEYE — SUPPORTED EVM CHAINS  🌐 🌐 🌐")
    print("=" * 75)
    print(f"{'Key':<14} {'Chain':<20} {'Chain ID':<10} {'Symbol':<8} {'RPC':<25}")
    print("-" * 75)

    for key, chain in sorted(EVM_CHAINS.items()):
        status = "✅" if chain.enabled else "❌"
        rpc_short = chain.rpc_url.replace("https://", "")[:24]
        print(f"{status} {key:<12} {chain.name:<20} {chain.chain_id:<10} "
              f"{chain.symbol:<8} {rpc_short:<25}")

    print("-" * 75)
    print(f"Total: {len(EVM_CHAINS)} EVM chains")

    if args.show_all:
        print("\n🔗 Explorer APIs:")
        for key, chain in sorted(EVM_CHAINS.items()):
            print(f"  {chain.emoji} {chain.name}: {chain.explorer_api}")

        print("\n🔤 Aliases:")
        for alias, target in sorted(ALIASES.items()):
            print(f"  {alias} → {target}")


def manage_patterns(args):
    """List, show, add, or remove detection patterns."""
    config = load_config()
    patterns = get_all_patterns(config)

    if args.action == "list":
        print(f"\n{'ID':<8} {'Severity':<10} {'Name':<35} {'Status':<10}")
        print("-" * 65)
        for pid, p in sorted(patterns.items()):
            status = "✅" if p.get("enabled", True) else "❌"
            print(f"{pid:<8} {p.get('severity', 'N/A'):<10} "
                  f"{p.get('name', 'N/A'):<35} {status:<10}")

    elif args.action == "show":
        if not args.pattern_id:
            logger.error("❌ Specify pattern ID to show")
            return
        p = patterns.get(args.pattern_id)
        if not p:
            logger.error(f"❌ Pattern '{args.pattern_id}' not found")
            return
        print(json.dumps(p, indent=2))

    elif args.action == "add":
        logger.info("📥 To add a pattern, create a YAML file in scanner/patterns/new/")
        logger.info("📋 Then run: python -m scanner.main reindex")

    elif args.action == "remove":
        logger.warning("⚠️  Pattern removal is disabled in safe mode")
        logger.info("📋 To disable a pattern, set 'enabled: false' in its config")


def run_validate(args):
    """Validate patterns against test cases or real contracts."""
    from scanner.engine import ScanEngine

    config = load_config()
    patterns = get_all_patterns(config)

    if args.all_patterns:
        logger.info(f"🧪 Validating {len(patterns)} patterns...")
        from scanner.tests.validator import validate_patterns
        results = validate_patterns(patterns)
        print(results)

    if args.pattern:
        if args.pattern not in patterns:
            logger.error(f"❌ Pattern '{args.pattern}' not found")
            return
        from scanner.tests.validator import validate_pattern
        result = validate_pattern(args.pattern, patterns[args.pattern])
        print(result)

    if args.contract:
        engine = ScanEngine()
        result = engine.scan([args.contract])
        print(result.to_text())


def run_reindex(args=None):
    """Re-index all patterns from the patterns directory."""
    from scanner.utils.config import build_pattern_index
    count = build_pattern_index()
    logger.info(f"✅ Re-indexed {count} patterns")


if __name__ == "__main__":
    main()
