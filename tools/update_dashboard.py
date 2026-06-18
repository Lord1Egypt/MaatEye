#!/usr/bin/env python3
"""
MaatEye — Dashboard JSON Updater
Converts scan results JSON → docs/dashboard.json consumed by the live GitHub Pages dashboard.
Does NOT touch docs/index.html — the static page is already generated.

Usage:
    python tools/update_dashboard.py --input results/cross_chain_report.json --output docs/dashboard.json
    python tools/update_dashboard.py --from-registry --output docs/dashboard.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def from_scan_report(report_path: str) -> dict:
    """Build dashboard.json from a scan report JSON file."""
    with open(report_path) as f:
        data = json.load(f)

    chain_summary = {}
    for chain_key, chain_data in data.get("chain_summary", {}).items():
        chain_summary[chain_key] = {
            "chain_name":  chain_data.get("chain_name", chain_key.title()),
            "chain_emoji": chain_data.get("chain_emoji", "⛓️"),
            "contracts":   chain_data.get("contracts", 0),
            "vulns":       chain_data.get("vulns", 0),
            "critical":    chain_data.get("critical", 0),
            "high":        chain_data.get("high", 0),
            "medium":      chain_data.get("medium", 0),
            "low":         chain_data.get("low", 0),
        }

    return {
        "scan_date":       data.get("timestamp") or datetime.now(timezone.utc).isoformat(),
        "total_chains":    data.get("total_chains", len(chain_summary)),
        "total_contracts": data.get("total_contracts", 0),
        "total_vulns":     data.get("total_vulns", 0),
        "critical_count":  data.get("critical_count", 0),
        "high_count":      data.get("high_count", 0),
        "medium_count":    data.get("medium_count", 0),
        "low_count":       data.get("low_count", 0),
        "chain_summary":   chain_summary,
    }


def from_registry() -> dict:
    """Build dashboard.json from the live token registry (cumulative totals)."""
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from scanner.fetchers.token_store import get_store
    from scanner.chains import EVM_CHAINS

    store = get_store()
    chain_stats = store.get_chain_stats()

    total_contracts = sum(s["total"] for s in chain_stats.values())
    total_vulns = sum(s["with_vulns"] for s in chain_stats.values())
    critical_count = sum(s["critical"] for s in chain_stats.values())
    high_count = sum(s["high"] for s in chain_stats.values())

    chain_summary = {}
    for chain_key, stats in chain_stats.items():
        chain = EVM_CHAINS.get(chain_key)
        chain_summary[chain_key] = {
            "chain_name":  chain.name if chain else chain_key.title(),
            "chain_emoji": chain.emoji if chain else "⛓️",
            "contracts":   stats["total"],
            "vulns":       stats["with_vulns"],
            "critical":    stats["critical"],
            "high":        stats["high"],
            "medium":      0,
            "low":         0,
        }

    return {
        "scan_date":       datetime.now(timezone.utc).isoformat(),
        "total_chains":    len(chain_stats),
        "total_contracts": total_contracts,
        "total_vulns":     total_vulns,
        "critical_count":  critical_count,
        "high_count":      high_count,
        "medium_count":    0,
        "low_count":       0,
        "chain_summary":   chain_summary,
    }


def merge_with_existing(new_data: dict, existing_path: str) -> dict:
    """
    Merge new scan data with existing dashboard.json using CUMULATIVE totals.
    New scan data wins for per-chain breakdowns; totals are accumulated.
    """
    existing = {}
    p = Path(existing_path)
    if p.exists():
        try:
            existing = json.loads(p.read_text())
        except Exception:
            pass

    if not existing:
        return new_data

    merged_chains = dict(existing.get("chain_summary", {}))
    for chain_key, chain_data in new_data.get("chain_summary", {}).items():
        if chain_key in merged_chains:
            ex = merged_chains[chain_key]
            merged_chains[chain_key] = {
                "chain_name":  chain_data["chain_name"],
                "chain_emoji": chain_data["chain_emoji"],
                "contracts":   max(ex.get("contracts", 0), chain_data["contracts"]),
                "vulns":       ex.get("vulns", 0) + chain_data["vulns"],
                "critical":    ex.get("critical", 0) + chain_data["critical"],
                "high":        ex.get("high", 0) + chain_data["high"],
                "medium":      ex.get("medium", 0) + chain_data["medium"],
                "low":         ex.get("low", 0) + chain_data["low"],
            }
        else:
            merged_chains[chain_key] = chain_data

    return {
        "scan_date":       new_data["scan_date"],
        "total_chains":    len(merged_chains),
        "total_contracts": max(
            existing.get("total_contracts", 0),
            new_data.get("total_contracts", 0),
        ),
        "total_vulns":     sum(c.get("vulns", 0) for c in merged_chains.values()),
        "critical_count":  sum(c.get("critical", 0) for c in merged_chains.values()),
        "high_count":      sum(c.get("high", 0) for c in merged_chains.values()),
        "medium_count":    sum(c.get("medium", 0) for c in merged_chains.values()),
        "low_count":       sum(c.get("low", 0) for c in merged_chains.values()),
        "chain_summary":   merged_chains,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Update docs/dashboard.json from scan results or registry"
    )
    parser.add_argument("--input", help="Path to scan report JSON (cross_chain_report.json)")
    parser.add_argument("--from-registry", action="store_true",
                        help="Build from live token registry instead of scan report")
    parser.add_argument("--output", default="docs/dashboard.json",
                        help="Output path for dashboard.json")
    parser.add_argument("--merge", action="store_true", default=True,
                        help="Merge with existing dashboard.json (cumulative mode)")
    args = parser.parse_args()

    if not args.input and not args.from_registry:
        parser.error("Provide either --input or --from-registry")

    print(f"📊 MaatEye Dashboard Updater")
    print(f"{'='*40}")

    if args.from_registry:
        print("📂 Building from token registry...")
        new_data = from_registry()
    else:
        if not Path(args.input).exists():
            print(f"❌ Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        print(f"📂 Loading scan report: {args.input}")
        new_data = from_scan_report(args.input)

    if args.merge:
        print(f"🔀 Merging with existing {args.output}...")
        final_data = merge_with_existing(new_data, args.output)
    else:
        final_data = new_data

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(final_data, indent=2, ensure_ascii=False))

    print(f"✅ Dashboard JSON updated: {args.output}")
    print(f"   Chains:     {final_data['total_chains']}")
    print(f"   Contracts:  {final_data['total_contracts']}")
    print(f"   Vulns:      {final_data['total_vulns']}")
    print(f"   Critical:   {final_data['critical_count']}")
    print(f"   High:       {final_data['high_count']}")


if __name__ == "__main__":
    main()
