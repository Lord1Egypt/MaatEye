#!/usr/bin/env python3
"""
🏗️ MaatEye — GitHub Pages Dashboard Generator (v2)
Generates from REAL token registry data.
Usage:
    python tools/generate_full_dashboard.py [--output docs/]
"""

import os, sys, json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent
DOCS_DIR = BASE / "docs"
REGISTRY_PATH = BASE / "data" / "token_registry.json"


def main():
    output_dir = DOCS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # Use from_registry in update_dashboard
    sys.path.insert(0, str(BASE))
    from tools.update_dashboard import from_registry
    from tools.generate_dashboard import generate_html

    data = from_registry()

    # Write dashboard.json
    json_path = output_dir / "dashboard.json"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"✅ Written: dashboard.json ({json_path.stat().st_size} bytes)")

    # Write index.html
    html = generate_html(data)
    index_path = output_dir / "index.html"
    index_path.write_text(html)
    print(f"✅ Written: index.html ({index_path.stat().st_size} bytes)")

    # Ensure .nojekyll
    (output_dir / ".nojekyll").write_text("")

    total_chains = data.get("total_chains", 0)
    total_contracts = data.get("total_contracts", 0)
    total_vulns = data.get("total_vulns", 0)
    print(f"\n📊 Dashboard Summary:")
    print(f"   Chains: {total_chains}")
    print(f"   Contracts: {total_contracts}")
    print(f"   Vulns: {total_vulns}")
    print(f"   Critical: {data.get('critical_count', 0)}")
    print(f"   High: {data.get('high_count', 0)}")


if __name__ == "__main__":
    main()
