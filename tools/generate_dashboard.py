#!/usr/bin/env python3
"""
🏗️ MaatEye — GitHub Pages Dashboard Generator
Converts scan results JSON → static HTML dashboard for GitHub Pages.

Usage:
    python tools/generate_dashboard.py --input results/cross_chain_report.json --output docs/
    python tools/generate_dashboard.py --demo --output docs/    # Placeholder with sample data
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


def get_demo_data() -> dict:
    """Generate demo/placeholder scan data for initial deploy."""
    return {
        "scan_date": datetime.now(timezone.utc).isoformat(),
        "total_chains": 24,
        "total_contracts": 1250,
        "total_vulns": 347,
        "critical_count": 23,
        "high_count": 89,
        "medium_count": 125,
        "low_count": 110,
        "chain_summary": {
            "ethereum": {"chain_name": "Ethereum", "chain_emoji": "💎", "contracts": 150, "vulns": 52, "critical": 5, "high": 14, "medium": 18, "low": 15},
            "bnb": {"chain_name": "BNB Smart Chain", "chain_emoji": "🟡", "contracts": 180, "vulns": 78, "critical": 8, "high": 22, "medium": 28, "low": 20},
            "polygon": {"chain_name": "Polygon", "chain_emoji": "🟣", "contracts": 120, "vulns": 31, "critical": 2, "high": 8, "medium": 12, "low": 9},
            "arbitrum": {"chain_name": "Arbitrum", "chain_emoji": "🔵", "contracts": 90, "vulns": 22, "critical": 1, "high": 5, "medium": 8, "low": 8},
            "optimism": {"chain_name": "Optimism", "chain_emoji": "🔴", "contracts": 70, "vulns": 18, "critical": 1, "high": 4, "medium": 7, "low": 6},
            "base": {"chain_name": "Base", "chain_emoji": "🔷", "contracts": 60, "vulns": 15, "critical": 1, "high": 3, "medium": 6, "low": 5},
        },
    }


def generate_html(data: dict) -> str:
    """Generate the complete dashboard HTML."""
    total = data.get("total_vulns", 0)
    critical = data.get("critical_count", 0)
    high = data.get("high_count", 0)
    medium = data.get("medium_count", 0)
    low = data.get("low_count", 0)
    chains = data.get("chain_summary", {})
    total_contracts = data.get("total_contracts", 0)
    total_chains = data.get("total_chains", 0)
    scan_date = data.get("scan_date", "N/A")

    # Build chain cards HTML
    chain_cards = ""
    for key, info in sorted(chains.items()):
        vuln_class = "chain-critical" if info["critical"] >= 5 else "chain-high" if info["high"] >= 10 else "chain-ok"
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
                <div class="bar-critical" style="width:{info['critical'] / max(info['vulns'], 1) * 100:.1f}%"></div>
                <div class="bar-high" style="width:{info['high'] / max(info['vulns'], 1) * 100:.1f}%"></div>
                <div class="bar-medium" style="width:{info['medium'] / max(info['vulns'], 1) * 100:.1f}%"></div>
            </div>
        </div>"""

    # Generate severity meter
    meter = f"""
    <div class="meter-container">
        <div class="meter-bar">
            <div class="meter-critical" style="width:{critical / max(total, 1) * 100:.1f}%">{critical}</div>
            <div class="meter-high" style="width:{high / max(total, 1) * 100:.1f}%">{high}</div>
            <div class="meter-medium" style="width:{medium / max(total, 1) * 100:.1f}%">{medium}</div>
            <div class="meter-low" style="width:{low / max(total, 1) * 100:.1f}%">{low}</div>
        </div>
    </div>"""

    # Build per-chain table rows
    table_rows = ""
    for key, info in sorted(chains.items(), key=lambda x: x[1]["vulns"], reverse=True):
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

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>👁️⚖️ MaatEye — Vulnerability Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0e1a;
            color: #e0e0e0;
            min-height: 100vh;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        
        /* Header */
        .header {{
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, #1a1f3a 0%, #0d1225 100%);
            border-bottom: 2px solid #2a3f6a;
            margin-bottom: 30px;
        }}
        .header h1 {{ font-size: 2.5em; color: #ffd700; margin-bottom: 10px; }}
        .header h1 span {{ color: #e0e0e0; }}
        .header p {{ color: #888; font-size: 1.1em; }}
        .header .subtitle {{ color: #4a7fc7; font-size: 0.9em; margin-top: 5px; }}
        
        /* Stats Overview */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #131a30;
            border: 1px solid #1e2d50;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: transform 0.2s;
        }}
        .stat-card:hover {{ transform: translateY(-2px); }}
        .stat-card .number {{ font-size: 2.2em; font-weight: bold; }}
        .stat-card .label {{ color: #888; font-size: 0.85em; text-transform: uppercase; letter-spacing: 1px; margin-top: 5px; }}
        .stat-card.total .number {{ color: #ffd700; }}
        .stat-card.critical .number {{ color: #ff4444; }}
        .stat-card.high .number {{ color: #ff8800; }}
        .stat-card.medium .number {{ color: #4488ff; }}
        .stat-card.low .number {{ color: #88cc88; }}
        .stat-card.chains .number {{ color: #aa88ff; }}
        .stat-card.contracts .number {{ color: #44ddff; }}

        /* Meter */
        .meter-container {{ margin-bottom: 30px; }}
        .meter-bar {{ display: flex; height: 36px; border-radius: 18px; overflow: hidden; }}
        .meter-critical {{ background: #ff4444; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.8em; transition: width 1s; }}
        .meter-high {{ background: #ff8800; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.8em; transition: width 1s; }}
        .meter-medium {{ background: #4488ff; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.8em; transition: width 1s; }}
        .meter-low {{ background: #44aa44; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.8em; transition: width 1s; }}

        /* Chain Cards */
        .chain-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .chain-card {{
            background: #131a30;
            border: 1px solid #1e2d50;
            border-radius: 12px;
            padding: 16px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .chain-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 20px rgba(0,0,0,0.4); }}
        .chain-card.chain-critical {{ border-left: 3px solid #ff4444; }}
        .chain-card.chain-high {{ border-left: 3px solid #ff8800; }}
        .chain-card.chain-ok {{ border-left: 3px solid #44aa44; }}
        .chain-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }}
        .chain-header .chain-emoji {{ font-size: 1.8em; }}
        .chain-header h3 {{ font-size: 1em; flex: 1; }}
        .chain-header .chain-key {{ font-size: 0.7em; color: #555; background: #0a0e1a; padding: 2px 8px; border-radius: 10px; }}
        .chain-stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }}
        .stat {{ text-align: center; padding: 4px; }}
        .stat .stat-label {{ display: block; font-size: 0.65em; color: #666; }}
        .stat .stat-value {{ font-size: 1.1em; font-weight: bold; }}
        .stat.critical .stat-value {{ color: #ff4444; }}
        .stat.high .stat-value {{ color: #ff8800; }}
        .stat.medium .stat-value {{ color: #4488ff; }}
        .vuln-bar {{ margin-top: 10px; height: 4px; display: flex; border-radius: 2px; overflow: hidden; background: #1a1f3a; }}
        .vuln-bar .bar-critical {{ background: #ff4444; }}
        .vuln-bar .bar-high {{ background: #ff8800; }}
        .vuln-bar .bar-medium {{ background: #4488ff; }}

        /* Table */
        .table-container {{ overflow-x: auto; margin-bottom: 30px; }}
        table {{ width: 100%; border-collapse: collapse; background: #131a30; border-radius: 12px; overflow: hidden; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #1e2d50; }}
        th {{ background: #0d1225; color: #ffd700; font-weight: 600; text-transform: uppercase; font-size: 0.8em; letter-spacing: 0.5px; }}
        td.critical, td.high, td.medium {{ font-weight: bold; }}
        td.critical {{ color: #ff4444; }}
        td.high {{ color: #ff8800; }}
        td.medium {{ color: #4488ff; }}
        tr:hover {{ background: #1a2340; }}

        /* Footer */
        .footer {{
            text-align: center;
            padding: 20px;
            color: #555;
            font-size: 0.85em;
            border-top: 1px solid #1e2d50;
            margin-top: 40px;
        }}
        .footer a {{ color: #4a7fc7; text-decoration: none; }}
        .footer a:hover {{ text-decoration: underline; }}

        /* Responsive */
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 1.8em; }}
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .chain-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>👁️⚖️ Maat<span>Eye</span></h1>
        <p>Multi-Chain Vulnerability Scanner — Live Dashboard</p>
        <div class="subtitle">📡 Last scan: {scan_date[:19].replace('T', ' ')} UTC</div>
    </div>

    <div class="container">
        <!-- Stats Cards -->
        <div class="stats-grid">
            <div class="stat-card total">
                <div class="number">{total}</div>
                <div class="label">Total Vulnerabilities</div>
            </div>
            <div class="stat-card critical">
                <div class="number">{critical}</div>
                <div class="label">🔴 Critical</div>
            </div>
            <div class="stat-card high">
                <div class="number">{high}</div>
                <div class="label">🟡 High</div>
            </div>
            <div class="stat-card medium">
                <div class="number">{medium}</div>
                <div class="label">🔵 Medium</div>
            </div>
            <div class="stat-card low">
                <div class="number">{low}</div>
                <div class="label">🟢 Low</div>
            </div>
            <div class="stat-card chains">
                <div class="number">{total_chains}</div>
                <div class="label">EVM Chains</div>
            </div>
            <div class="stat-card contracts">
                <div class="number">{total_contracts}</div>
                <div class="label">Contracts Scanned</div>
            </div>
        </div>

        <!-- Severity Meter -->
        <h2 style="color: #ffd700; margin-bottom: 10px;">📊 Severity Distribution</h2>
        {meter}

        <!-- Chain Cards -->
        <h2 style="color: #ffd700; margin: 30px 0 15px;">🌐 Per-Chain Breakdown</h2>
        <div class="chain-grid">
            {chain_cards}
        </div>

        <!-- Full Table -->
        <h2 style="color: #ffd700; margin: 30px 0 15px;">📋 Chain Comparison</h2>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Chain</th>
                        <th>Contracts</th>
                        <th>Total Vulns</th>
                        <th>🔴 Critical</th>
                        <th>🟡 High</th>
                        <th>🔵 Medium</th>
                        <th>🟢 Low</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
    </div>

    <div class="footer">
        <p>👁️⚖️ <a href="https://github.com/Lord1Egypt/MaatEye">MaatEye</a> — Automated with 💙 by Lord1Egypt</p>
        <p>Data refreshes daily at 08:00 UTC • Static analysis only — read-only, no exploits</p>
        <p>🔗 <a href="https://github.com/Lord1Egypt/MaatEye">GitHub</a></p>
    </div>
</body>
</html>"""
    return html


def main():
    parser = argparse.ArgumentParser(description="Generate MaatEye GitHub Pages dashboard")
    parser.add_argument("--input", help="Path to scan results JSON")
    parser.add_argument("--output", default="docs", help="Output directory")
    parser.add_argument("--demo", action="store_true", help="Generate demo dashboard with sample data")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine data source
    if args.demo:
        data = get_demo_data()
        print("📊 Generating demo dashboard...")
    elif args.input:
        if not Path(args.input).exists():
            print(f"❌ Input file not found: {args.input}")
            sys.exit(1)
        data = load_scan_results(args.input)
        print(f"📊 Generating dashboard from {args.input}...")
    else:
        print("❌ Need either --input or --demo")
        sys.exit(1)

    # Generate HTML
    html = generate_html(data)

    # Write files
    index_path = output_dir / "index.html"
    index_path.write_text(html)
    print(f"✅ Dashboard written to {index_path}")

    # Write raw data for potential JS consumption
    data_path = output_dir / "dashboard.json"
    data_path.write_text(json.dumps(data, indent=2))
    print(f"✅ Dashboard data written to {data_path}")

    # Create .nojekyll for GitHub Pages
    (output_dir / ".nojekyll").write_text("")
    print(f"✅ .nojekyll created")

    print(f"\n🌍 Open dashboard: file://{index_path.absolute()}")
    print(f"🌍 GitHub Pages: https://lord1egypt.github.io/MaatEye/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
