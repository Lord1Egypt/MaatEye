#!/usr/bin/env python3
"""
🏗️ MaatEye — GitHub Pages Dashboard Generator
Generates a FULL dashboard: stats, pattern categories, all 50 patterns,
per-chain breakdown, and chain comparison table — ALL from REAL data.

Usage:
    python tools/generate_dashboard.py --input dashboard.json --output docs/
    python tools/generate_dashboard.py --demo --output docs/    # ⚠️ DEPRECATED
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_scan_results(path: str) -> dict:
    """Load scan results from JSON file."""
    with open(path) as f:
        return json.load(f)


# ═══════════════════════════════════════════════════════════════════
# 🏗️ HTML GENERATOR — Full Dashboard with ALL sections
# ═══════════════════════════════════════════════════════════════════

SEVERITY_COLORS = {
    "critical": "#ff4444",
    "high": "#ff8800",
    "medium": "#4488ff",
    "low": "#44cc44",
}
SEVERITY_EMOJI = {
    "critical": "🔴",
    "high": "🟡",
    "medium": "🔵",
    "low": "🟢",
}


def generate_html(data: dict) -> str:
    """Generate the complete dashboard HTML — ALL sections, REAL data."""

    # ── Top-level stats ────────────────────────────────────────────────
    total = data.get("total_vulns", 0)
    critical = data.get("critical_count", 0)
    high = data.get("high_count", 0)
    medium = data.get("medium_count", 0)
    low = data.get("low_count", 0)
    total_contracts = data.get("total_contracts", 0)
    total_chains = data.get("total_chains", 0)
    scan_date = data.get("scan_date", "N/A")
    pattern_count = data.get("pattern_count", 0)
    pattern_categories = data.get("pattern_categories", {})
    patterns = data.get("patterns", [])
    chains = data.get("chain_summary", {})

    # ── Pattern Severity Distribution (count by severity) ──────────────
    p_crit = sum(1 for p in patterns if p.get("severity") == "critical")
    p_high = sum(1 for p in patterns if p.get("severity") == "high")
    p_med = sum(1 for p in patterns if p.get("severity") == "medium")
    p_low = sum(1 for p in patterns if p.get("severity") == "low")

    # ── Pattern meter ─────────────────────────────────────────────────
    p_total = max(pattern_count, 1)
    pat_meter = f"""
    <div class="meter-container" style="margin-top:5px;">
        <div class="meter-bar" style="height:28px;border-radius:14px;">
            <div class="meter-critical" style="width:{p_crit/p_total*100:.1f}%">{p_crit}</div>
            <div class="meter-high" style="width:{p_high/p_total*100:.1f}%">{p_high}</div>
            <div class="meter-medium" style="width:{p_med/p_total*100:.1f}%">{p_med}</div>
        </div>
    </div>"""

    # ── Vulns meter (hide when 0) ─────────────────────────────────────
    if total > 0:
        vuln_meter = f"""
        <div class="meter-container">
            <div class="meter-bar">
                <div class="meter-critical" style="width:{critical/max(total,1)*100:.1f}%">{critical:,}</div>
                <div class="meter-high" style="width:{high/max(total,1)*100:.1f}%">{high:,}</div>
                <div class="meter-medium" style="width:{medium/max(total,1)*100:.1f}%">{medium:,}</div>
                <div class="meter-low" style="width:{low/max(total,1)*100:.1f}%">{low:,}</div>
            </div>
        </div>"""
    else:
        vuln_meter = '<div class="meter-container"><div class="meter-bar"><div class="meter-low" style="width:100%">0 findings — clean 🛡️</div></div></div>'

    # Highest pattern ID
    max_pat_id = max((p.get("id", "P00") for p in patterns), default="P00")
    cat_blocks = ""
    cat_order = sorted(pattern_categories.items(), key=lambda x: -x[1])
    for cat, count in cat_order:
        cat_blocks += f"""
        <div class="cat-block">
            <div class="cat-name">{cat}</div>
            <div class="cat-count">{count}</div>
        </div>"""

    # ── Pattern List ("The 50 Plagues") ────────────────────────────────
    pattern_rows = ""
    for p in patterns:
        sev = p.get("severity", "medium")
        sev_color = SEVERITY_COLORS.get(sev, "#888")
        sev_emoji = SEVERITY_EMOJI.get(sev, "⚪")
        sev_label = sev.upper()
        pattern_rows += f"""
            <div class="pat-row pat-{sev}">
                <span class="pat-id">{p.get('id','??')}</span>
                <span class="pat-name">{p.get('name','Unknown')}</span>
                <span class="pat-cat-tag">{p.get('category','OTHER')}</span>
                <span class="pat-sev" style="background:{sev_color}30;color:{sev_color};border:1px solid {sev_color}50;">{sev_emoji} {sev_label}</span>
            </div>"""

    # ── Chain Cards ────────────────────────────────────────────────────
    chain_cards = ""
    for key, info in sorted(chains.items()):
        has_vulns = info.get("vulns", 0) > 0
        if has_vulns:
            vuln_class = "chain-red" if info["critical"] >= 5 else "chain-orange" if info["high"] >= 10 else "chain-green"
        else:
            vuln_class = "chain-none"
        # bar widths
        v = max(info["vulns"], 1)
        chain_cards += f"""
        <div class="chain-card {vuln_class}">
            <div class="chain-header">
                <span class="chain-emoji">{info['chain_emoji']}</span>
                <h3>{info['chain_name']}</h3>
                <span class="chain-key">{key}</span>
            </div>
            <div class="chain-stats">
                <div class="stat"><span class="stat-label">Contracts</span><span class="stat-value">{info['contracts']}</span></div>
                <div class="stat"><span class="stat-label">Vulns</span><span class="stat-value">{info['vulns']}</span></div>
                <div class="stat critical"><span class="stat-label">🔴 Critical</span><span class="stat-value">{info['critical']}</span></div>
                <div class="stat high"><span class="stat-label">🟡 High</span><span class="stat-value">{info['high']}</span></div>
                <div class="stat medium"><span class="stat-label">🔵 Medium</span><span class="stat-value">{info['medium']}</span></div>
            </div>
            <div class="vuln-bar">
                <div class="bar-critical" style="width:{info['critical']/v*100:.1f}%"></div>
                <div class="bar-high" style="width:{info['high']/v*100:.1f}%"></div>
                <div class="bar-medium" style="width:{info['medium']/v*100:.1f}%"></div>
            </div>
        </div>"""

    # ── Chain Comparison Table ─────────────────────────────────────────
    table_rows = ""
    for key, info in sorted(chains.items(), key=lambda x: -x[1]["vulns"]):
        table_rows += f"""
        <tr>
            <td>{info['chain_emoji']} {info['chain_name']}</td>
            <td>{info['contracts']}</td>
            <td>{info['vulns']}</td>
            <td class="critical">{info['critical']}</td>
            <td class="high">{info['high']}</td>
            <td class="medium">{info['medium']}</td>
            <td>{info['low']}</td>
        </tr>"""

    # formatted scan date
    try:
        dt = scan_date[:19].replace("T", " ")
    except Exception:
        dt = scan_date

    # ═══════════════════════════════════════════════════════════════════
    # 🏗️ FINAL HTML
    # ═══════════════════════════════════════════════════════════════════
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>👁️⚖️ MaatEye — Vulnerability Dashboard</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; background:#0a0e1a; color:#e0e0e0; min-height:100vh; }}
.container {{ max-width:1400px; margin:0 auto; padding:20px; }}

/* ═══ HEADER ═══ */
.header {{ text-align:center; padding:40px 20px; background:linear-gradient(135deg,#1a1f3a 0%,#0d1225 100%); border-bottom:2px solid #2a3f6a; margin-bottom:30px; }}
.header h1 {{ font-size:2.5em; color:#ffd700; margin-bottom:10px; }}
.header h1 span {{ color:#e0e0e0; }}
.header p {{ color:#888; font-size:1.1em; }}
.header .subtitle {{ color:#4a7fc7; font-size:0.9em; margin-top:5px; }}
.badge {{ display:inline-block; background:linear-gradient(135deg,#ffd700,#ff8c00); color:#0a0e1a; font-weight:bold; padding:4px 16px; border-radius:20px; font-size:0.85em; margin-top:10px; }}

/* ═══ STATS CARDS ═══ */
.stats-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:15px; margin-bottom:30px; }}
.stat-card {{ background:#131a30; border:1px solid #1e2d50; border-radius:12px; padding:20px; text-align:center; transition:transform .2s; }}
.stat-card:hover {{ transform:translateY(-2px); }}
.stat-card .number {{ font-size:2em; font-weight:bold; }}
.stat-card .label {{ color:#888; font-size:0.8em; text-transform:uppercase; letter-spacing:1px; margin-top:5px; }}
.stat-card.total .number {{ color:#ffd700; }}
.stat-card.critical .number {{ color:#ff4444; }}
.stat-card.high .number {{ color:#ff8800; }}
.stat-card.medium .number {{ color:#4488ff; }}
.stat-card.low .number {{ color:#88cc88; }}
.stat-card.chains .number {{ color:#aa88ff; }}
.stat-card.contracts .number {{ color:#44ddff; }}
.stat-card.patterns .number {{ color:#ff66aa; }}

/* ═══ METER ═══ */
.meter-container {{ margin-bottom:25px; }}
.meter-bar {{ display:flex; height:36px; border-radius:18px; overflow:hidden; }}
.meter-critical {{ background:#ff4444; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:.8em; transition:width 1s; }}
.meter-high {{ background:#ff8800; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:.8em; transition:width 1s; }}
.meter-medium {{ background:#4488ff; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:.8em; transition:width 1s; }}
.meter-low {{ background:#44aa44; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:.8em; transition:width 1s; }}

/* ═══ PATTERN CATEGORIES ═══ */
.cat-grid {{ display:flex; flex-wrap:wrap; gap:10px; margin-bottom:30px; }}
.cat-block {{ background:#131a30; border:1px solid #1e2d50; border-radius:10px; padding:12px 18px; text-align:center; min-width:120px; flex:1; }}
.cat-name {{ font-size:0.75em; color:#888; text-transform:uppercase; letter-spacing:.5px; }}
.cat-count {{ font-size:1.6em; font-weight:bold; color:#ffd700; }}

/* ═══ PATTERN LIST (50 Plagues) ═══ */
.pat-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(380px,1fr)); gap:8px; margin-bottom:30px; }}
.pat-row {{ display:flex; align-items:center; gap:8px; background:#131a30; border:1px solid #1e2d50; border-radius:8px; padding:8px 12px; transition:background .15s; }}
.pat-row:hover {{ background:#1a2340; }}
.pat-id {{ font-family:monospace; font-weight:bold; color:#ffd700; min-width:38px; }}
.pat-name {{ flex:1; font-size:0.9em; }}
.pat-cat-tag {{ font-size:0.65em; color:#666; background:#0a0e1a; padding:2px 8px; border-radius:8px; white-space:nowrap; }}
.pat-sev {{ font-size:0.7em; font-weight:bold; padding:2px 10px; border-radius:10px; white-space:nowrap; }}

/* ═══ CHAIN CARDS ═══ */
.chain-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:15px; margin-bottom:30px; }}
.chain-card {{ background:#131a30; border:1px solid #1e2d50; border-radius:12px; padding:16px; transition:transform .2s,box-shadow .2s; }}
.chain-card:hover {{ transform:translateY(-2px); box-shadow:0 4px 20px rgba(0,0,0,.4); }}
.chain-card.chain-red {{ border-left:3px solid #ff4444; }}
.chain-card.chain-orange {{ border-left:3px solid #ff8800; }}
.chain-card.chain-green {{ border-left:3px solid #44aa44; }}
.chain-card.chain-none {{ border-left:3px solid #2a3f6a; }}
.chain-header {{ display:flex; align-items:center; gap:10px; margin-bottom:12px; }}
.chain-header .chain-emoji {{ font-size:1.8em; }}
.chain-header h3 {{ font-size:1em; flex:1; }}
.chain-header .chain-key {{ font-size:0.7em; color:#555; background:#0a0e1a; padding:2px 8px; border-radius:10px; }}
.chain-stats {{ display:grid; grid-template-columns:repeat(3,1fr); gap:6px; }}
.stat {{ text-align:center; padding:4px; }}
.stat .stat-label {{ display:block; font-size:0.65em; color:#666; }}
.stat .stat-value {{ font-size:1.1em; font-weight:bold; }}
.stat.critical .stat-value {{ color:#ff4444; }}
.stat.high .stat-value {{ color:#ff8800; }}
.stat.medium .stat-value {{ color:#4488ff; }}
.vuln-bar {{ margin-top:10px; height:4px; display:flex; border-radius:2px; overflow:hidden; background:#1a1f3a; }}
.vuln-bar .bar-critical {{ background:#ff4444; }}
.vuln-bar .bar-high {{ background:#ff8800; }}
.vuln-bar .bar-medium {{ background:#4488ff; }}

/* ═══ TABLE ═══ */
.table-container {{ overflow-x:auto; margin-bottom:30px; }}
table {{ width:100%; border-collapse:collapse; background:#131a30; border-radius:12px; overflow:hidden; }}
th, td {{ padding:12px 16px; text-align:left; border-bottom:1px solid #1e2d50; }}
th {{ background:#0d1225; color:#ffd700; font-weight:600; text-transform:uppercase; font-size:.8em; letter-spacing:.5px; }}
td.critical, td.high, td.medium {{ font-weight:bold; }}
td.critical {{ color:#ff4444; }}
td.high {{ color:#ff8800; }}
td.medium {{ color:#4488ff; }}
tr:hover {{ background:#1a2340; }}

/* ═══ SECTION HEADERS ═══ */
.section-title {{ color:#ffd700; margin:30px 0 15px; display:flex; align-items:center; gap:10px; }}
.section-sub {{ color:#4a7fc7; font-size:0.85em; margin:-10px 0 15px; }}

/* ═══ FOOTER ═══ */
.footer {{ text-align:center; padding:20px; color:#555; font-size:.85em; border-top:1px solid #1e2d50; margin-top:40px; }}
.footer a {{ color:#4a7fc7; text-decoration:none; }}
.footer a:hover {{ text-decoration:underline; }}

/* ═══ RESPONSIVE ═══ */
@media (max-width:768px) {{ .header h1 {{ font-size:1.8em; }} .stats-grid {{ grid-template-columns:repeat(2,1fr); }} .chain-grid {{ grid-template-columns:1fr; }} .pat-grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>

<div class="header">
    <h1>👁️⚖️ Maat<span>Eye</span></h1>
    <p>Multi-Chain Vulnerability Scanner — Live Dashboard</p>
    <div class="subtitle">📡 Last scan: {dt} UTC</div>
    <div class="badge">⚖️ {pattern_count} Detection Patterns across {len(pattern_categories)} Categories</div>
</div>

<div class="container">

    <!-- ═══ STATS CARDS ═══ -->
    <div class="stats-grid">
        <div class="stat-card total"><div class="number">{total:,}</div><div class="label">Total Findings</div></div>
        <div class="stat-card critical"><div class="number">{critical:,}</div><div class="label">🔴 Contracts w/ Critical</div></div>
        <div class="stat-card high"><div class="number">{high:,}</div><div class="label">🟡 Contracts w/ High</div></div>
        <div class="stat-card medium"><div class="number">{medium:,}</div><div class="label">🔵 Contracts w/ Medium</div></div>
        <div class="stat-card low"><div class="number">{low:,}</div><div class="label">🟢 Contracts w/ Low</div></div>
        <div class="stat-card chains"><div class="number">{total_chains}</div><div class="label">EVM Chains</div></div>
        <div class="stat-card contracts"><div class="number">{total_contracts:,}</div><div class="label">Contracts Scanned</div></div>
        <div class="stat-card patterns"><div class="number">{pattern_count}</div><div class="label">Detection Patterns</div></div>
    </div>

    <!-- ═══ VULNERABILITY METER ═══ -->
    <h2 class="section-title">📊 Severity Distribution (Vulnerabilities)</h2>
    {vuln_meter}

    <!-- ═══ PATTERN CATEGORIES ═══ -->
    <h2 class="section-title">📂 Pattern Categories</h2>
    <div class="cat-grid">
        {cat_blocks}
    </div>

    <!-- ═══ PATTERN SEVERITY (Patterns) ═══ -->
    <h2 class="section-title">📊 Pattern Severity Distribution ({pattern_count} Patterns)</h2>
    <p class="section-sub">🔴 {p_crit} Critical · 🟡 {p_high} High · 🔵 {p_med} Medium</p>
    {pat_meter}

    <!-- ═══ THE 50 PLAGUES ═══ -->
    <h2 class="section-title">⚡️ The {pattern_count} Plagues — Detection Patterns</h2>
    <p class="section-sub">Every pattern MaatEye checks, from P01 to {max_pat_id} — {len(patterns)} total</p>
    <div class="pat-grid">
        {pattern_rows}
    </div>

    <!-- ═══ PER-CHAIN CARDS ═══ -->
    <h2 class="section-title">🌐 Per-Chain Breakdown</h2>
    <div class="chain-grid">
        {chain_cards}
    </div>

    <!-- ═══ CHAIN COMPARISON TABLE ═══ -->
    <h2 class="section-title">📋 Chain Comparison</h2>
    <div class="table-container">
        <table>
            <thead>
                <tr><th>Chain</th><th>Contracts</th><th>Total Vulns</th><th>🔴 Critical</th><th>🟡 High</th><th>🔵 Medium</th><th>🟢 Low</th></tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>

</div>

<div class="footer">
    <p>👁️⚖️ <a href="https://github.com/Lord1Egypt/MaatEye">MaatEye</a> — {pattern_count} Patterns · {total_chains} Chains · Automated with 💙 by Lord1Egypt</p>
    <p>𝝛 v0.5 Pattern Explosion — From 20 to 50 patterns in one session 🔥</p>
    <p>Data refreshes daily at 08:00 UTC • Static analysis only — read-only, no exploits</p>
    <p>🔗 <a href="https://github.com/Lord1Egypt/MaatEye">GitHub</a> · Dashboard</p>
</div>

</body>
</html>"""


# ═══════════════════════════════════════════════════════════════════
# 🚀 CLI
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Generate MaatEye GitHub Pages dashboard")
    parser.add_argument("--input", help="Path to dashboard.json (from from_registry)")
    parser.add_argument("--output", default="docs", help="Output directory")
    parser.add_argument("--demo", action="store_true", help="⚠️ DEPRECATED — generates demo (fake) data")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.demo:
        # Build a minimal data skeleton so the HTML doesn't crash
        data = {
            "scan_date": datetime.now(timezone.utc).isoformat(),
            "total_chains": 0,
            "total_contracts": 0,
            "total_vulns": 0,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "pattern_count": 50,
            "pattern_categories": {
                "ACCESS_CONTROL": 9, "REENTRANCY": 8, "EXTERNAL_CALLS": 8,
                "PROXY_UPGRADEABLE": 7, "ARITHMETIC": 5, "TOKEN_ECONOMICS": 5,
                "GOVERNANCE": 3, "BUSINESS_LOGIC": 3, "ERC_STANDARDS": 1,
                "SIGNATURE_CRYPTO": 1,
            },
            "patterns": [
                {"id": f"P{i:02d}", "name": "Placeholder Pattern", "severity": "medium",
                 "category": "OTHER", "difficulty": "medium"}
                for i in range(1, 51)
            ],
            "chain_summary": {},
        }
        print("⚠️  DEPRECATED: --demo generates skeleton data. Use --input with real dashboard.json instead.")
    elif args.input:
        if not Path(args.input).exists():
            print(f"❌ Input not found: {args.input}")
            sys.exit(1)
        data = load_scan_results(args.input)
    else:
        print("❌ Need --input <dashboard.json>")
        sys.exit(1)

    html = generate_html(data)

    index_path = output_dir / "index.html"
    index_path.write_text(html)
    print(f"✅ index.html written ({index_path.stat().st_size} bytes)")

    # Also save dashboard.json when generating from input
    if args.input and not args.demo:
        data_path = output_dir / "dashboard.json"
        data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        print(f"✅ dashboard.json written ({data_path.stat().st_size} bytes)")

    (output_dir / ".nojekyll").write_text("")
    print("✅ .nojekyll created")
    print(f"\n🌍 file://{index_path.absolute()}")


if __name__ == "__main__":
    sys.exit(main())
