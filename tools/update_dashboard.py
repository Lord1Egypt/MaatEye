#!/usr/bin/env python3
"""
👁️⚖️ MaatEye — Dashboard Generator
Generates dashboard.json from the REAL token registry + patterns.
Two modes:
  1. Direct:  python tools/update_dashboard.py
  2. Import:  from_registry()  → used by hourly_scan.py
"""

import os, sys, json, yaml
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent
PATTERNS_DIR = BASE / "scanner" / "patterns"
DOCS_DIR = BASE / "docs"
REGISTRY_PATH = BASE / "data" / "token_registry.json"


def load_patterns() -> dict:
    """Load all pattern YAMLs → categories + severity counts."""
    yaml_files = sorted(PATTERNS_DIR.glob("P*.yaml"))
    cats = {}
    sev_count = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    patterns_list = []

    for f in yaml_files:
        try:
            p = yaml.safe_load(f.read_text())
        except Exception:
            continue
        if not p:
            continue
        cat = p.get("category", "OTHER")
        cats.setdefault(cat, []).append(p["id"])
        sev = p.get("severity", "medium")
        if sev in sev_count:
            sev_count[sev] += 1
        patterns_list.append({
            "id": p["id"],
            "name": p["name"],
            "severity": sev,
            "category": cat,
            "difficulty": p.get("difficulty", "medium"),
        })

    return {"patterns_list": patterns_list, "cats": cats, "sev_count": sev_count,
            "total_patterns": sum(sev_count.values())}


def from_registry() -> dict:
    """
    Generate dashboard data from the REAL token registry.
    Used by hourly_scan.py → build_dashboard_json().
    """
    # ── Pattern info ────────────────────────────────────────────────────
    pinfo = load_patterns()
    sev = pinfo["sev_count"]

    # ── Load real token registry ────────────────────────────────────────
    registry = {}
    registry_path = str(REGISTRY_PATH)
    if os.path.exists(registry_path):
        with open(registry_path) as f:
            registry = json.load(f)

    total_tokens = sum(len(v) for v in registry.values())
    total_chains = len(registry)

    # ── Build chain summary from registry ────────────────────────────────
    CHAIN_META = {
        "ethereum":  {"name": "Ethereum",     "emoji": "💎"},
        "bnb":       {"name": "BNB Chain",     "emoji": "🟡"},
        "polygon":   {"name": "Polygon",       "emoji": "🟣"},
        "arbitrum":  {"name": "Arbitrum One",  "emoji": "🌀"},
        "optimism":  {"name": "Optimism",      "emoji": "🔴"},
        "base":      {"name": "Base",          "emoji": "🔷"},
        "avalanche": {"name": "Avalanche C-Chain", "emoji": "🔺"},
        "linea":     {"name": "Linea",         "emoji": "⬛"},
        "scroll":    {"name": "Scroll",        "emoji": "📜"},
        "blast":     {"name": "Blast",         "emoji": "💥"},
        "gnosis":    {"name": "Gnosis",        "emoji": "🦉"},
        "celo":      {"name": "Celo",          "emoji": "🌿"},
        "moonbeam":  {"name": "Moonbeam",      "emoji": "🌕"},
        "metis":     {"name": "Metis",         "emoji": "🏛"},
        "opbnb":     {"name": "opBNB",         "emoji": "🟨"},
        "pulsechain":{"name": "PulseChain",    "emoji": "💓"},
        "mantle":    {"name": "Mantle",        "emoji": "⚙️"},
        "taiko":     {"name": "Taiko",         "emoji": "🥁"},
        "berachain": {"name": "Berachain",     "emoji": "🐻"},
        "soneium":   {"name": "Soneium",       "emoji": "🌊"},
        "unichain":  {"name": "Unichain",      "emoji": "🦄"},
        "fraxtal":   {"name": "Fraxtal",       "emoji": "⬜"},
        "chiliz":    {"name": "Chiliz",        "emoji": "🌶"},
        "sonic":     {"name": "Sonic",         "emoji": "⚡"},
    }

    chain_summary = {}
    total_vulns = 0
    total_crit = 0
    total_high = 0
    total_med = 0
    total_low = 0

    for chain_key, tokens in sorted(registry.items()):
        meta = CHAIN_META.get(chain_key, {"name": chain_key.title(), "emoji": "🌐"})

        # Count actual scan data from tokens if available
        chain_vulns = 0
        chain_crit = 0
        chain_high = 0
        chain_med = 0
        chain_low = 0

        # Use severity info from registry if stored
        for addr, info in tokens.items():
            if isinstance(info, dict):
                max_sev = info.get("max_severity", "")
                vcount = info.get("vuln_count", 0)
                if vcount:
                    chain_vulns += vcount
                if max_sev == "critical":
                    chain_crit += 1
                elif max_sev == "high":
                    chain_high += 1
                elif max_sev == "medium":
                    chain_med += 1
                elif max_sev == "low":
                    chain_low += 1

        # If no scan data yet, report 0 vulns (honest)
        # Don't estimate — avoid inflating numbers
        if chain_vulns == 0:
            pass  # Report 0 vulns, which is the truth

        total_vulns += chain_vulns
        total_crit += chain_crit
        total_high += chain_high
        total_med += chain_med
        total_low += chain_low

        chain_summary[chain_key] = {
            "chain_name": meta["name"],
            "chain_emoji": meta["emoji"],
            "contracts": len(tokens),
            "vulns": chain_vulns,
            "critical": chain_crit,
            "high": chain_high,
            "medium": chain_med,
            "low": chain_low,
        }

    # If no chains in registry, show patterns as fallback
    if not chain_summary:
        chain_summary["ethereum"] = {
            "chain_name": "Ethereum",
            "chain_emoji": "💎",
            "contracts": 0,
            "vulns": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }
        total_chains = 1

    data = {
        "scan_date": datetime.now(timezone.utc).isoformat(),
        "total_chains": total_chains,
        "total_contracts": total_tokens,
        "total_vulns": total_vulns,
        "critical_count": total_crit,
        "high_count": total_high,
        "medium_count": total_med,
        "low_count": total_low,
        "pattern_count": pinfo["total_patterns"],
        "pattern_categories": {cat: len(ids) for cat, ids in sorted(pinfo["cats"].items())},
        "patterns": pinfo["patterns_list"],
        "chain_summary": chain_summary,
    }

    return data


def main():
    """Direct execution: update dashboard.json AND index.html from real data."""
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from tools.generate_dashboard import generate_html

    data = from_registry()

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DOCS_DIR / "dashboard.json"
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    # Also regenerate index.html
    html = generate_html(data)
    index_path = DOCS_DIR / "index.html"
    index_path.write_text(html)

    total = data["total_contracts"]
    vulns = data["total_vulns"]
    chains = data["total_chains"]
    print(f"✅ dashboard.json + index.html updated — {chains} chains, {total} contracts, {vulns} vulns")
    print(f"   Patterns: {data['pattern_count']}")
    print(f"   Severity: 🔴{data['critical_count']} 🟡{data['high_count']} 🔵{data['medium_count']}")


if __name__ == "__main__":
    main()
