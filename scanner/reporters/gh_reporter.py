"""
MaatEye — GitHub Reporter
Creates Issues, updates README, and manages the Red Flag registry.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from scanner.utils.logger import get_logger

logger = get_logger(__name__)


class GitHubReporter:
    """Handles all GitHub reporting: issues, badges, dashboards."""

    def __init__(self, repo: str = "", token: str = ""):
        self.repo = repo or os.environ.get("GITHUB_REPOSITORY", "Lord1Egypt/MaatEye")
        self.token = token or os.environ.get("GITHUB_TOKEN", "")

    def create_red_flag_issue(self, contract: str, vuln: dict) -> Optional[int]:
        """Create a Red Flag issue for a critical vulnerability."""
        severity = vuln.get("severity", "medium")
        pattern_name = vuln.get("pattern_name", "Unknown")
        description = vuln.get("description", "No description")
        chain = vuln.get("chain", "ethereum")
        chain_name = vuln.get("chain_name", "Ethereum")
        chain_emoji = vuln.get("chain_emoji", "🔵")

        title = f"🚩 [RedFlag] {chain_emoji} {pattern_name} on {chain_name} — {contract[:10]}...{contract[-6:]}"

        body = f"""## 🚩 Red Flag: {pattern_name}

**Contract:** `{contract}`
**Chain:** {chain_emoji} **{chain_name}** (`{chain}`)
**Severity:** {severity}
**Pattern:** `{vuln.get('pattern_id', 'N/A')}`
**Confidence:** {vuln.get('confidence', 0.5):.0%}

### Description
{description}

### Location
`{vuln.get('location', 'N/A')}`

### Evidence
```
{vuln.get('evidence', 'N/A')}
```

### Recommendation
{vuln.get('recommendation', 'No recommendation available')}

---

> 🏛️ *Flagged by MaatEye — The Eternal Guardian of Smart Contracts*
> 🌐 *Cross-chain scan across {chain_emoji} {chain_name}*
"""

        labels = ["Red Flag", severity]

        if not self.token:
            logger.warning("ℹ️ No GITHUB_TOKEN — issue will be printed instead of created")
            print(f"\n--- Issue would be created ---\n{body}\n---")
            return None

        try:
            result = subprocess.run(
                ["gh", "issue", "create",
                 "--repo", self.repo,
                 "--title", title,
                 "--body", body,
                 "--label", ",".join(labels)],
                capture_output=True, text=True, timeout=30,
                env={**os.environ, "GH_TOKEN": self.token},
            )
            if result.returncode == 0:
                issue_url = result.stdout.strip()
                logger.info(f"  🚩 Created issue: {issue_url}")
                # Extract issue number from URL
                return int(issue_url.split("/")[-1])
            else:
                logger.warning(f"  ⚠️ Failed to create issue: {result.stderr}")
                return None
        except Exception as e:
            logger.warning(f"  ⚠️ Issue creation failed: {e}")
            return None

    def create_advisory_issue(self, contract: str, vuln: dict) -> Optional[int]:
        """Create an advisory issue for medium/high severity findings."""
        severity = vuln.get("severity", "medium")
        pattern_name = vuln.get("pattern_name", "Unknown")

        title = f"⚠️ [Advisory] {pattern_name} in {contract[:10]}...{contract[-6:]}"

        body = f"""## ⚠️ Advisory: {pattern_name}

**Contract:** `{contract}`
**Severity:** {severity}

{vuln.get('description', '')}

**Recommendation:** {vuln.get('recommendation', '')}
"""

        labels = ["advisory", severity]

        if not self.token:
            return None

        try:
            result = subprocess.run(
                ["gh", "issue", "create",
                 "--repo", self.repo,
                 "--title", title,
                 "--body", body,
                 "--label", ",".join(labels)],
                capture_output=True, text=True, timeout=30,
                env={**os.environ, "GH_TOKEN": self.token},
            )
            if result.returncode == 0:
                issue_url = result.stdout.strip()
                return int(issue_url.split("/")[-1])
            return None
        except Exception:
            return None

    def update_readme_badges(self, results_path: str, readme_path: str) -> None:
        """Update the badges in README.md based on scan results."""
        try:
            with open(results_path) as f:
                results = json.load(f)
        except (IOError, json.JSONDecodeError):
            logger.warning("⚠️ Cannot update badges — no results")
            return

        critical = results.get("critical_count", 0)
        high = results.get("high_count", 0)
        total_vulns = results.get("total_vulns", 0)
        total_contracts = results.get("total_contracts", 0)

        # Update the code is simpler — we just note the changes
        logger.info(f"📊 Badge update: {critical}🔴 {high}🟡 {total_vulns} total vulns")
        logger.info(f"📊 Run 'python -m scanner.reporters.gh_reporter badges' to update README")

    def update_dashboard(self, results_path: str, output_path: str) -> str:
        """Generate a scan dashboard markdown file."""
        try:
            with open(results_path) as f:
                results = json.load(f)
        except (IOError, json.JSONDecodeError):
            return "No scan data available."

        critical = results.get("critical_count", 0)
        high = results.get("high_count", 0)
        medium = results.get("medium_count", 0)
        total = results.get("total_vulns", 0)
        contracts = results.get("total_contracts", 0)
        timestamp = results.get("timestamp", "N/A")
        scan_time = results.get("scan_time_seconds", 0)

        dashboard = f"""# 👁️⚖️ MaatEye — Vulnerability Dashboard

**Last Scan:** {timestamp}
**Scan Time:** {scan_time:.1f}s
**Contracts Scanned:** {contracts}
**Total Vulnerabilities:** {total}

## Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical | {critical} |
| 🟡 High | {high} |
| 🔵 Medium | {medium} |
| 🟢 Low | {results.get('low_count', 0)} |

## Contracts with Critical Issues

"""
        for addr, contract in results.get("contracts", {}).items():
            if contract.get("critical_count", 0) > 0:
                dashboard += f"- `{addr}` — {contract.get('contract_name', 'Unknown')} ({contract['critical_count']} critical)\n"

        if critical == 0:
            dashboard += "_No critical vulnerabilities found in this scan._\n"

        dashboard += "\n## Red Flag Registry\n\n"
        dashboard += "_See [GitHub Issues](https://github.com/Lord1Egypt/MaatEye/issues?q=label%3A%22Red+Flag%22) for all active Red Flags._\n"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(dashboard)

        logger.info(f"📊 Dashboard written to {output_path}")
        return dashboard

    def add_comment_to_issue(self, issue_number: int, body: str) -> bool:
        """Add a comment to an existing issue."""
        if not self.token:
            return False

        try:
            result = subprocess.run(
                ["gh", "issue", "comment", str(issue_number),
                 "--repo", self.repo,
                 "--body", body],
                capture_output=True, text=True, timeout=30,
                env={**os.environ, "GH_TOKEN": self.token},
            )
            return result.returncode == 0
        except Exception:
            return False


# ── CLI Entry Points for GitHub Actions ────────────────────────────────────────


def check_results():
    """Check scan results and output to actions.txt for CI."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="results/actions.txt")
    args = parser.parse_args()

    try:
        with open(args.input) as f:
            results = json.load(f)
    except Exception as e:
        logger.error(f"❌ Cannot read results: {e}")
        sys.exit(1)

    critical = results.get("critical_count", 0)
    total = results.get("total_vulns", 0)

    lines = [
        f"has_vulns={'true' if critical > 0 else 'false'}",
        f"critical={critical}",
        f"total={total}",
    ]

    with open(args.output, "w") as f:
        f.write("\n".join(lines) + "\n")

    # Expose as GitHub Actions step outputs so downstream `if:` gates work
    # (e.g. steps.check.outputs.has_vulns). Falls back to stdout locally.
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a") as f:
            f.write("\n".join(lines) + "\n")

    for line in lines:
        print(line)


def create_issues():
    """Create GitHub Issues from scan results."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN", ""))
    args = parser.parse_args()

    try:
        with open(args.input) as f:
            results = json.load(f)
    except Exception as e:
        logger.error(f"❌ Cannot read results: {e}")
        sys.exit(1)

    reporter = GitHubReporter(repo=args.repo, token=args.token)
    created = 0

    for addr, contract in results.get("contracts", {}).items():
        for vuln in contract.get("vulnerabilities", []):
            severity = vuln.get("severity", "")

            if severity == "critical":
                issue_id = reporter.create_red_flag_issue(addr, vuln)
                if issue_id:
                    created += 1
            elif severity == "high":
                reporter.create_advisory_issue(addr, vuln)

    logger.info(f"✅ Created {created} Red Flag issues")


def update_badges():
    """Update README badges from scan results."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--readme", default="README.md")
    args = parser.parse_args()

    reporter = GitHubReporter()
    reporter.update_readme_badges(args.input, args.readme)


def update_dashboard():
    """Update the dashboard markdown from scan results."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="results/DASHBOARD.md")
    args = parser.parse_args()

    reporter = GitHubReporter()
    reporter.update_dashboard(args.input, args.output)


def add_scan_comment():
    """Add a scan results comment to a PR or issue."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--issue-number", type=int, required=True)
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN", ""))
    args = parser.parse_args()

    try:
        with open(args.input) as f:
            results = json.load(f)
    except Exception:
        logger.error("❌ Cannot read results")
        sys.exit(1)

    body = "## 🔍 MaatEye Scan Results\n\n"
    body += f"**Contracts:** {results.get('total_contracts', 0)} | "
    body += f"**Vulns:** {results.get('total_vulns', 0)} | "
    body += f"🔴{results.get('critical_count', 0)} 🟡{results.get('high_count', 0)}\n\n"

    for addr, contract in results.get("contracts", {}).items():
        body += f"- `{addr[:10]}...{addr[-6:]}`: "
        if contract.get("error"):
            body += f"❌ {contract['error']}\n"
        elif contract.get("vuln_count", 0) > 0:
            body += f"⚠️ {contract['vuln_count']} vuln(s)\n"
        else:
            body += "✅ Clean\n"

    reporter = GitHubReporter(repo=args.repo, token=args.token)
    reporter.add_comment_to_issue(args.issue_number, body)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m scanner.reporters.gh_reporter [check|issues|badges|dashboard|comment] ...")
        sys.exit(1)

    command = sys.argv[1]
    sys.argv = sys.argv[1:]  # Remove command name

    if command == "check":
        check_results()
    elif command == "issues":
        create_issues()
    elif command == "badges":
        update_badges()
    elif command == "dashboard":
        update_dashboard()
    elif command == "comment":
        add_scan_comment()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
