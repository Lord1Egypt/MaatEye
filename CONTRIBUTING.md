# 🤝 Contributing to MaatEye

We're building the most comprehensive open-source smart contract vulnerability scanner — and we need **you**.

## Ways to Contribute

### ✨ Add a New Pattern
1. Fork the repo
2. Create a YAML file in `scanner/patterns/new/` named `PXX_your_pattern.yaml`
3. Follow the pattern template
4. Open a PR — CI will validate it
5. Once merged, the pattern registry auto-updates 🪄

**Pattern Template:**
```yaml
id: "P21"
name: "Your Pattern Name"
severity: "critical"  # critical, high, medium, low
enabled: true
description: "What does this detect and why is it dangerous?"
detectors:
  - type: "regex"
    description: "Brief description"
    pattern: "your_regex_pattern"
    confidence: 0.85
    recommendation: "How to fix it"
```

### 🐛 Report a Bug
Open an issue with the `bug` label.

### 🔍 Submit a Contract
Open an issue with the `scan-request` label and include the contract address.

### 📖 Improve Documentation
Even a typo fix helps!

## Development Setup

```bash
git clone https://github.com/Lord1Egypt/MaatEye.git
cd MaatEye
pip install -r requirements.txt
python -m scanner.main patterns list
```

## Pattern Guidelines
- **False positives are OK** — we'd rather flag a safe contract than miss a vulnerable one
- **Confidence scores matter** — be honest about detection reliability
- **Include recommendations** — tell people how to fix it
- **Reference real incidents** — SWC IDs, CVE numbers, hack examples

## PR Process
1. PRs need 1 approval from a maintainer
2. CI must pass (tests + pattern validation)
3. New patterns auto-register on merge

## Code of Conduct
Be excellent to each other. This project is for learning, protecting, and building.
