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

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "scan":
        run_scan(args)
    elif args.command == "patterns":
        manage_patterns(args)
    elif args.command == "validate":
        run_validate(args)
    elif args.command == "reindex":
        run_reindex(args)


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
        Path(args.output).write_text(output)
        logger.info(f"✅ Results written to {args.output}")
    else:
        print(output)

    # Return non-zero if critical vulns found (for CI)
    if results.critical_count > 0:
        sys.exit(0)  # Don't fail CI for findings — just report


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


def run_reindex():
    """Re-index all patterns from the patterns directory."""
    from scanner.utils.config import build_pattern_index
    count = build_pattern_index()
    logger.info(f"✅ Re-indexed {count} patterns")


if __name__ == "__main__":
    main()
