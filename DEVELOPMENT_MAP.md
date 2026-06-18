# 👁️⚖️ MaatEye — Full Development Map

> **Purpose:** This document is the single source of truth for continuing development after any session limit.
> Load this file at the start of every new session: `@DEVELOPMENT_MAP.md`

---

## 🗺️ Project Overview

| Property | Value |
|---|---|
| **Repo** | https://github.com/Lord1Egypt/MaatEye |
| **GitHub Pages** | https://lord1egypt.github.io/MaatEye/ |
| **Language** | Python 3.11+ |
| **CI/CD** | GitHub Actions (`.github/workflows/`) |
| **Scan Engine** | `scanner/engine.py` |
| **Dashboard** | `docs/index.html` (auto-deployed via Pages) |

### Architecture Quick Reference
```
MaatEye/
├── scanner/
│   ├── engine.py           # Core scan engine + result models
│   ├── main.py             # CLI entrypoint (argparse)
│   ├── chains/             # 24 EVM chain definitions
│   ├── fetchers/           # Source code fetchers (etherscan, multichain, rpc, local)
│   ├── patterns/           # 20 Plague detection pattern YAMLs/JSONs
│   ├── reporters/          # Output formatters (markdown, JSON, badge)
│   ├── utils/              # Config loader, logger
│   └── tests/              # Unit tests
├── docs/                   # GitHub Pages (deployed from /docs)
│   ├── index.html          # Live dashboard (reads dashboard.json)
│   ├── dashboard.json      # Scan results — auto-updated by CI
│   └── ROADMAP.md          # Short roadmap summary
├── config/                 # Config files
├── tools/                  # Helper scripts
├── tests/                  # Integration tests
└── .github/workflows/      # GitHub Actions CI
```

---

## 🐛 Bugs Fixed (Session 1 — 2026-06-18)

- [x] **`scanner/engine.py` — Duplicate `ScanResults` fields** (lines 83-92 had 5 fields declared twice)
- [x] **`scanner/engine.py` — `_apply_pattern` missing `self` and `result`** (wrong method signature)
- [x] **`docs/index.html` — Basic placeholder dashboard** (rewritten as full Egyptian-themed live dashboard)

---

## Phase 1 — Foundation Fixes 🔧
**Goal:** Make the scanner actually run end-to-end without errors.
**Status:** 🔄 In Progress

### Checklist
- [x] Fix `ScanResults` duplicate fields in `engine.py`
- [x] Fix `_apply_pattern` method signature in `engine.py`
- [x] Rebuild `docs/index.html` as a stunning live dashboard
- [ ] Audit all pattern YAML/JSON files for completeness — check `scanner/patterns/` for all 20 entries
- [ ] Verify `scanner/main.py` CLI commands work — run `python -m scanner.main --help`
- [ ] Verify `scanner/fetchers/etherscan.py` — check API key handling, error paths
- [ ] Verify `scanner/fetchers/multichain.py` — handles missing API keys gracefully
- [ ] Verify `scanner/fetchers/token_discovery.py` — CoinGecko fetch, RPC event log scan, dedup
- [ ] Verify `scanner/chains/__init__.py` — `get_chain()`, `list_chains()` return correct types
- [ ] Verify `scanner/utils/config.py` — `load_config()`, `get_all_patterns()` return expected shapes
- [ ] Run unit tests — `python -m pytest scanner/tests/ -v`
- [ ] Syntax check all Python — `find scanner -name "*.py" | xargs python3 -m py_compile`

---

## Phase 2 — Scanner Completion 🔬
**Goal:** All 20 Plagues patterns complete, real scanner runs on a sample contract.

### Checklist — Pattern Engine
- [ ] Audit all 20 pattern definitions in `scanner/patterns/`
- [ ] Complete any missing patterns (P01–P20 all need YAML entries)
- [ ] Test each pattern against a known-vulnerable contract snippet
- [ ] Add pattern tests in `scanner/tests/test_patterns.py`

### Checklist — Source Fetcher
- [ ] `scanner/fetchers/etherscan.py` — confirm return shape `{source_code, contract_name, compiler, chain, chain_name}`
- [ ] `scanner/fetchers/multichain.py` — test against BNB, Polygon, Arbitrum
- [ ] `scanner/fetchers/token_discovery.py`:
  - [ ] CoinGecko import (`import --coingecko`)
  - [ ] RPC event log import (`import --rpc`)
  - [ ] Dedup logic (same address on same chain = skip)
  - [ ] Registry persistence (`data/token_registry.json`)
- [ ] Rate limiting — all fetchers respect rate limits
- [ ] Timeout handling — all HTTP calls have explicit `timeout=` param

### Checklist — CLI Commands
Run these manually and verify output:
- [ ] `python -m scanner.main scan --address 0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18`
- [ ] `python -m scanner.main chains`
- [ ] `python -m scanner.main tokens stats`
- [ ] `python -m scanner.main scan-chain bnb --count 5`
- [ ] `python -m scanner.main scan-all --tokens-per-chain 5`

---

## Phase 3 — GitHub Actions Automation ⚙️
**Goal:** Fully automated daily scans that update `docs/dashboard.json` and create Issues.

### Checklist
- [ ] Read existing `.github/workflows/scan-scheduled.yml`
- [ ] Confirm workflow runs at 08:00 UTC daily
- [ ] Confirm it saves to `docs/dashboard.json` and commits
- [ ] Add `workflow_dispatch` manual trigger
- [ ] Test by manually triggering from Actions tab
- [ ] Fix any permission errors (Actions needs write access)
- [ ] Add RPC event log workflow for new token discovery
- [ ] Add weekly full scan workflow (15K+ tokens)
- [ ] Verify GitHub Issue reporter works (`scanner/reporters/github_issues.py`)

---

## Phase 4 — GitHub Pages Dashboard Polish 🎨
**Goal:** Dashboard at https://lord1egypt.github.io/MaatEye/ is stunning and live.

### Checklist
- [x] Rebuild `docs/index.html` with Egyptian-themed design
- [x] Animated Eye of Ra logo
- [x] Live stats loading from `dashboard.json`
- [x] Severity distribution animated bar
- [x] Per-chain breakdown cards
- [x] Chain comparison table
- [x] 20 Plagues pattern showcase
- [x] Hieroglyph particle background
- [ ] Add search/filter to chain table
- [ ] Add scan history chart (vuln count over time)
- [ ] Add "recently flagged contracts" section (from GitHub Issues API)
- [ ] Add GitHub Actions status badge
- [ ] Mobile responsiveness polish
- [ ] Add `docs/favicon.ico` (Egyptian Eye icon)
- [ ] **Enable GitHub Pages** in repo Settings → Pages → Source: `main`, `/docs` folder

### How to Enable GitHub Pages
1. Go to https://github.com/Lord1Egypt/MaatEye/settings/pages
2. Source: Deploy from branch
3. Branch: `main`, Folder: `/docs`
4. Save — site deploys to https://lord1egypt.github.io/MaatEye/

---

## Phase 5 — Community & Documentation 📚

### Checklist
- [ ] Add GitHub Pages link at top of README
- [ ] Add screenshots/demo GIF of dashboard
- [ ] Fix README truncated pattern table (cuts off at P11)
- [ ] Add all 20 patterns to README table
- [ ] Add "Quick Start" section with 3 commands
- [ ] Add API keys guide (which are needed, free sources)
- [ ] Fix Mermaid architecture diagram (currently plain text code block)
- [ ] Add contributing guide for new patterns
- [ ] Add pattern template YAML in `scanner/patterns/template.yml`
- [ ] Create `GEMINI.md` / `CLAUDE.md` — AI assistant engineering memory

---

## Phase 6 — Advanced Features 🚀

### Checklist
- [ ] False positive reduction — confidence scoring per pattern
- [ ] Context-aware patterns (e.g. check SafeMath before flagging overflow)
- [ ] Multi-file contract support
- [ ] Proxy detection + implementation analysis
- [ ] Bytecode analysis fallback (unverified contracts)
- [ ] ERC standards validation (ERC20, ERC721, ERC1155)
- [ ] TheGraph subgraph as Source 7
- [x] **DeFiLlama integration** — `scanner/fetchers/defillama.py` (Source 6)
- [x] **DexScreener integration** — `scanner/fetchers/dexscreener.py` (Source 5)
- [x] **Full 24-chain RPC event-log support** — All chains in `PERMISSIVE_RPCS`
- [x] **Archive node support** — For ethereum, polygon, gnosis, celo
- [ ] PDF report generation
- [ ] Badge generation for README embedding

---

## Phase 7 — Release 🌟

### Checklist
- [ ] Tag v1.0.0 release with release notes
- [ ] Add GitHub Topics: solidity, smart-contracts, security, web3, ethereum, vulnerability-scanner
- [ ] Submit to awesome-ethereum lists
- [ ] Write dev.to / Mirror.xyz article
- [ ] Community submission to EthSecurity newsletter

---

## 🚨 Known Issues (as of 2026-06-18 — Session 2)

| # | Issue | Severity | File | Status |
|---|---|---|---|---|
| 1 | Duplicate fields in `ScanResults` | 🔴 Critical | `scanner/engine.py:83-92` | ✅ Fixed |
| 2 | `_apply_pattern` missing `self`+`result` params | 🔴 Critical | `scanner/engine.py:525` | ✅ Fixed |
| 3 | README pattern table truncated at P11 | 🟡 Medium | `README.md:122` | ⏳ Pending |
| 4 | `docs/index.html` was basic placeholder | 🟡 Medium | `docs/index.html` | ✅ Fixed |
| 5 | GitHub Pages not confirmed enabled | 🟡 Medium | GitHub Settings | ⏳ Pending |
| 6 | No `GEMINI.md`/`CLAUDE.md` AI assistant memory | 🟢 Low | root | ⏳ Pending |
| 7 | No `favicon.ico` for GitHub Pages | 🟢 Low | `docs/` | ⏳ Pending |

---

## 📝 Session Resume Prompt

Copy this at the start of a new session:

```
Continue MaatEye (https://github.com/Lord1Egypt/MaatEye).
Read DEVELOPMENT_MAP.md for full context.
Phase 1 is done. Next: Phase 2 — audit scanner/patterns/ for all 20 pattern definitions.
```

---

## 🔗 References

- [GitHub Pages Docs](https://docs.github.com/en/pages)
- [Etherscan API](https://docs.etherscan.io/)
- [CoinGecko API](https://www.coingecko.com/en/api/documentation)
- [publicnode.com RPC](https://publicnode.com)
- [SWC Smart Contract Vulnerability Registry](https://swcregistry.io/)
- [Kesra — Reference GitHub Pages deployment](https://github.com/Lord1Egypt/Kesra)

---

*Last updated: 2026-06-18 by Antigravity AI*
*"May your contracts be balanced on the feather of Ma'at ⚖️"*
