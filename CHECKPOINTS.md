# 👁️⚖️ MaatEye — Session Checkpoints

> Complete log of all development work done across AI sessions.
> **Resume prompt:** *"Read CHECKPOINTS.md and DEVELOPMENT_MAP.md for full context."*

---

## Checkpoint 3 — 2026-06-18 (Session 1, Part 3)

### Repo Housekeeping
- Set repo `About → Website` to `https://lord1egypt.github.io/MaatEye/` via `gh repo edit`
- Set repo description: *"👁️⚖️ The Eternal Guardian of Smart Contracts — automated vulnerability scanner across 24 EVM chains with 20 detection patterns"*

### GitHub Pages Deployment — Fixed Conflict
| Problem | Root Cause | Fix |
|---------|-----------|-----|
| All deployments failing | `web-deploy.yml` used `actions/deploy-pages@v4` **conflicting** with native `/docs` branch Pages | Deleted `web-deploy.yml` entirely |
| `index.html` overwritten on every scan | `scan-scheduled.yml` called `generate_dashboard.py --output docs/` | Replaced with `update_dashboard.py --output docs/dashboard.json` (data only) |

### New Files Created
| File | Purpose |
|------|---------|
| `tools/update_dashboard.py` | Converts scan JSON → `dashboard.json`; supports cumulative merge mode |
| `tools/hourly_scan.py` | 4-phase hourly scanner: RPC discovery → register → scan → update dashboard |
| `.github/workflows/rpc-hourly-scan.yml` | Hourly GitHub Actions workflow |

### Hourly Scanner Architecture
```
Every hour at :05 UTC
       │
       ▼
Phase 1: RPC Discovery
  eth_getLogs Transfer events
  last ~1h of blocks per chain
  (300 blocks Ethereum, 1200 BNB, 1800 Polygon...)
       │
       ▼
Phase 2: Register New Tokens
  Filter against token_registry.json
  Only NEW addresses added (dedup)
  data/token_registry.json updated
       │
       ▼
Phase 3: Vulnerability Scan
  Fetch source code (Etherscan/Blockscout APIs)
  Run all 20 Plague patterns
  Up to 500 new tokens per chain
       │
       ▼
Phase 4: Update Dashboard
  Rebuild docs/dashboard.json from registry
  Commit + push → GitHub Pages auto-redeploys
```

### Commits
- `83b5eae` — feat: hourly RPC token scanner + fix Pages conflict

---

## Checkpoint 2 — 2026-06-18 (Session 1, Part 2)

### GitHub Pages — Enabled
- User enabled Pages in Settings → Branch: `main`, Folder: `/docs`
- Site live at: **https://lord1egypt.github.io/MaatEye/**
- Native `/docs` folder deployment (same approach as Kesra game)

---

## Checkpoint 1 — 2026-06-18 (Session 1, Part 1)

### Repository Analysis
Cloned `https://github.com/Lord1Egypt/MaatEye` and performed full audit:

**Architecture discovered:**
```
MaatEye/
├── scanner/
│   ├── engine.py           # Core engine — ScanEngine + result models
│   ├── main.py             # CLI (argparse, 8 subcommands)
│   ├── chains/__init__.py  # 24 EVM chain definitions with publicnode RPCs
│   ├── fetchers/
│   │   ├── etherscan.py        # Etherscan-compatible source fetcher
│   │   ├── multichain.py       # Multi-chain source fetcher
│   │   ├── rpc_discovery.py    # Transfer-event token discovery via RPC
│   │   ├── token_discovery.py  # Master discovery orchestrator (4 sources)
│   │   └── token_store.py      # Persistent JSON registry with dedup
│   ├── patterns/           # 20 Plague detection YAMLs (P01–P20)
│   ├── reporters/
│   │   └── gh_reporter.py  # GitHub Issues + dashboard reporter
│   └── utils/              # config.py, logger.py
├── docs/
│   ├── index.html          # GitHub Pages dashboard (rebuilt)
│   └── dashboard.json      # Live scan results (auto-updated by CI)
├── tools/
│   ├── generate_dashboard.py  # OLD — generates full HTML (legacy)
│   ├── update_dashboard.py    # NEW — updates only dashboard.json
│   └── hourly_scan.py         # NEW — hourly RPC scan orchestrator
└── .github/workflows/
    ├── scan-scheduled.yml      # Daily 08:00 UTC cross-chain scan
    ├── rpc-hourly-scan.yml     # NEW — hourly RPC token discovery
    ├── scan-on-demand.yml      # Manual trigger scan
    ├── self-update.yml         # Pattern self-update
    └── test-patterns.yml       # Pattern test suite
```

### Bugs Fixed

#### Bug 1 — `scanner/engine.py` — Duplicate `ScanResults` Fields (CRITICAL)
```python
# BEFORE (broken): 5 fields declared twice in the dataclass
@dataclass
class ScanResults:
    low_count: int = 0
    contracts: dict[str, ContractResult] = field(default_factory=dict)
    scan_time_seconds: float = 0.0
    timestamp: str = ""
    chains_scanned: list[str] = field(default_factory=list)
    low_count: int = 0                                           # ← DUPLICATE
    contracts: dict[str, ContractResult] = field(default_factory=dict)  # ← DUPLICATE
    scan_time_seconds: float = 0.0                              # ← DUPLICATE
    timestamp: str = ""                                         # ← DUPLICATE
    chains_scanned: list[str] = field(default_factory=list)    # ← DUPLICATE

# AFTER (fixed): duplicates removed
@dataclass
class ScanResults:
    low_count: int = 0
    contracts: dict[str, ContractResult] = field(default_factory=dict)
    scan_time_seconds: float = 0.0
    timestamp: str = ""
    chains_scanned: list[str] = field(default_factory=list)
```

#### Bug 2 — `scanner/engine.py` — `_apply_pattern` Wrong Method Signature (CRITICAL)
```python
# BEFORE (broken): missing self and result — crashes at runtime on result.contract_name
def _apply_pattern(
    pattern: dict,
    source_code: str,
    address: str,
    vulnerabilities: list,
):

# AFTER (fixed): correct instance method signature
def _apply_pattern(
    self,
    result: ContractResult,
    pattern: dict,
    source_code: str,
    address: str,
    vulnerabilities: list,
):
```

### `docs/index.html` — Complete Rewrite
Old: 383 lines, basic static HTML, hardcoded numbers, no JS, no animations.

New — full Egyptian-themed live dashboard:
| Feature | Details |
|---------|---------|
| **Theme** | Dark `#05060F` bg, gold `#FFD700`, teal `#00D4AA` accents |
| **Logo** | Animated SVG Eye of Ra / Maat scales with gold glow pulse |
| **Loading screen** | "MAAT IS WATCHING" with pulsing eye |
| **Particles** | Hieroglyph characters (𓂀𓃭𓆙𓅓) floating up via canvas |
| **Stats** | 7 KPI cards with counter animations, loaded from `dashboard.json` |
| **Severity bar** | Animated proportional bar (Critical/High/Medium/Low) |
| **Chain cards** | Per-chain risk-coded cards with severity pills + mini bar chart |
| **Table** | Chain comparison with sortable columns + risk badges |
| **20 Plagues** | All 20 detection patterns displayed as cards with severity tags |
| **Fonts** | Inter + JetBrains Mono from Google Fonts |
| **Responsive** | Mobile-optimized grid layouts |

### `README.md` — Improvements
- Added prominent **Live Dashboard badge** linking to `lord1egypt.github.io/MaatEye/`
- Badge format: gold `#FFD700` on dark `#05060F`

### `DEVELOPMENT_MAP.md` — Created
Full 7-phase development roadmap with:
- Phase 1–7 checklists (Foundation → Scanner → CI → Dashboard → Docs → Advanced → Release)
- Bug tracker table
- Known issues log
- Architecture reference
- Session resume prompt

### Commits
- `3a02ff0` — fix: engine.py duplicate fields + method signature; feat: brilliant GitHub Pages dashboard; docs: DEVELOPMENT_MAP.md full roadmap

---

## Quick Reference — All Key Commands

```bash
# Run hourly scan manually
python tools/hourly_scan.py --max-new 500 --workers 10

# Discovery only (no source fetch)
python tools/hourly_scan.py --no-scan --max-new 1000

# Update dashboard from registry
python tools/update_dashboard.py --from-registry --output docs/dashboard.json

# Scan a specific address
python -m scanner.main scan --address 0x... --chain ethereum

# Scan top tokens on all chains (daily)
python -m scanner.main scan-all --tokens-per-chain 10

# View token registry stats
python -m scanner.main tokens stats

# List all 24 supported chains
python -m scanner.main chains
```

---

## Known Issues & Status (2026-06-18 — Session 2)

| # | Issue | File | Status |
|---|-------|------|--------|
| 1 | Duplicate `ScanResults` fields | `scanner/engine.py:83` | ✅ Fixed |
| 2 | `_apply_pattern` missing `self`+`result` | `scanner/engine.py:525` | ✅ Fixed |
| 3 | `web-deploy.yml` conflicting with Pages | `.github/workflows/` | ✅ Deleted |
| 4 | `index.html` overwritten by daily scan | `scan-scheduled.yml:104` | ✅ Fixed |
| 5 | Basic placeholder dashboard | `docs/index.html` | ✅ Rebuilt |
| 6 | No GitHub Pages link in repo About | GitHub Settings | ✅ Fixed |
| 7 | No hourly RPC scanner | `.github/workflows/` | ✅ Created |
| 8 | Patterns audit (P01–P20 completeness) | `scanner/patterns/` | ✅ Complete (20/20) |
| 9 | No `data/.gitkeep` for empty registry dir | `data/` | ✅ Added |
| 10 | `GEMINI.md`/`CLAUDE.md` AI memory file | root | ✅ Updated |
| 11 | RPC discovery only 7/24 chains | `rpc_discovery.py` | ✅ Expanded to 24 |
| 12 | No DexScreener integration | `scanner/fetchers/` | ✅ Created (Source 5) |
| 13 | No DeFiLlama integration | `scanner/fetchers/` | ✅ Created (Source 6) |
| 14 | Hourly scanner fallback weak | `hourly_scan.py` | ✅ 5-level cascade |
| 15 | No archive RPC support | `rpc_discovery.py` | ✅ Added for 4 chains |

---

## Links

| Resource | URL |
|----------|-----|
| Repository | https://github.com/Lord1Egypt/MaatEye |
| Live Dashboard | https://lord1egypt.github.io/MaatEye/ |
| Issues (Red Flags) | https://github.com/Lord1Egypt/MaatEye/issues |
| Actions | https://github.com/Lord1Egypt/MaatEye/actions |
| DEVELOPMENT_MAP.md | https://github.com/Lord1Egypt/MaatEye/blob/main/DEVELOPMENT_MAP.md |

---

---

## Checkpoint 4 — 2026-06-18 (Session 2 — Token Coverage Expansion)

### Session Goal
Expand token discovery from 7-chain RPC bottleneck to full 24-chain coverage + 2 new discovery sources (DexScreener, DeFiLlama) + archive node support.

### Improvements Implemented

#### 1. RPC Event-Log Discovery — Expanded to ALL 24 EVM Chains
`scanner/fetchers/rpc_discovery.py`:
- **Before:** `PERMISSIVE_RPCS` had only 7 chains (ethereum, bnb, polygon, arbitrum, optimism, base, avalanche)
- **After:** All 24 chains now have publicnode.com RPC endpoints for `eth_getLogs` Transfer event scanning
- Added `ARCHIVE_RPCS` for chains with archive node support (ethereum, polygon, gnosis, celo)
- Added secondary RPC fallbacks via Ankr/LlamaRPC for the top 7 high-volume chains

#### 2. New Source 5: DexScreener Token Discovery
`scanner/fetchers/dexscreener.py`:
- Pulls live token pairs from DexScreener API (`api.dexscreener.com/latest/dex/search`)
- Discovers tokens recently paired on DEXs across ALL chains — catches tokens before CoinGecko lists them
- Rate-limited (500ms between calls) with configurable maximum per chain

#### 3. New Source 6: DeFiLlama Token Discovery
`scanner/fetchers/defillama.py`:
- Pulls current token list from DeFiLlama's coin listing API
- Broader coverage than CoinGecko for newer chains and tokens
- Rate-limited with configurable maximum per chain

#### 4. Master Discovery Orchestrator Updated
`scanner/fetchers/token_discovery.py`:
- `discover_all_tokens()` now includes Source 5 (DexScreener) and Source 6 (DeFiLlama)
- All sources are deduplicated automatically

#### 5. Multi-Source Discovery Cascade in Hourly Scanner
`tools/hourly_scan.py`:
- **Before:** Only Ethereum had fallback (to 1.45M local DB), other chains had no fallback
- **After:** 5-level discovery cascade for ALL 24 chains:
  1. RPC event logs (eth_getLogs, real-time)
  2. CoinGecko API (15k+ tokens)
  3. DexScreener (newly boosted tokens)
  4. Ethereum local DB (1.45M addresses, ethereum only)
  5. Explorer API (top verified contracts)
- Each chain independently fails through the cascade until tokens are found

### Files Created
| File | Purpose |
|------|---------|
| `scanner/fetchers/dexscreener.py` | DexScreener API integration (Source 5) |
| `scanner/fetchers/defillama.py` | DeFiLlama API integration (Source 6) |

### Files Modified
| File | Change |
|------|--------|
| `scanner/fetchers/rpc_discovery.py` | All 24 chains in PERMISSIVE_RPCS + archive nodes |
| `scanner/fetchers/token_discovery.py` | Sources 5 & 6 integrated into master orchestrator |
| `tools/hourly_scan.py` | Expanded fallback logic for all chains |

### Test Results
- ✅ `python3 -m py_compile` on all modified/created files passes
- ✅ All 20 patterns load without errors
- ✅ `python -m scanner.main tokens stats` shows registry integrity
- ✅ Pattern engine loads all 45 detectors across 20 patterns

### Test Results
| Test | Result |
|------|--------|
| `py_compile` on all 28 Python files | ✅ All pass |
| `pytest tests/` (9 unit tests) | ✅ 9/9 pass |
| All 20 patterns load (45 detectors) | ✅ Loaded |
| Pattern engine | ✅ 20 patterns, 45 detectors |
| Token registry integrity | ✅ 5,914 tokens, 7 chains intact |

### Detailed File Changes

#### `scanner/fetchers/rpc_discovery.py`
- **PERMISSIVE_RPCS**: Expanded from 7 → 24 chains
  - Added: linea, scroll, blast, gnosis, celo, moonbeam, metis, opbnb, pulsechain, mantle, taiko, berachain, soneium, unichain, fraxtal, chiliz, sonic
  - Each chain has publicnode.com RPC as primary + fallbacks where available
- **ARCHIVE_RPCS**: Added real archive node support
  - ethereum: merkle.io, ankr
  - polygon: polygon-rpc.com
  - gnosis: publicnode
  - celo: forno.celo.org
- **discover_tokens_rpc_catchup()**: Auto-fallback to chain's own RPC URL from config when not in PERMISSIVE_RPCS
- **discover_tokens_rpc_all_chains()**: Uses ALL chains from EVM_CHAINS registry (not just PERMISSIVE_RPCS keys)

#### `scanner/fetchers/dexscreener.py` (NEW)
- Fetches `/token-boosts/latest/v1` and `/token-boosts/top/v1` from DexScreener
- Maps 24 DexScreener chain IDs → MaatEye chain keys
- Rate-limited (500ms interval), configurable max per chain
- Zero dependencies (uses urllib only)

#### `scanner/fetchers/defillama.py` (NEW)
- Fetches `/list` from DeFiLlama's coins API (500K+ entries)
- Maps chain IDs from DeFiLlama format → MaatEye keys
- Rate-limited (300ms interval), configurable max per chain (default 2000)
- Filters and validates EVM addresses only

#### `scanner/fetchers/token_discovery.py`
- Updated docstring: 6 sources (was 4)
- `discover_all_tokens()`: Added `use_dexscreener` and `use_defillama` params
- Sources 5 (DexScreener) and 6 (DeFiLlama) are called after the original 4
- All results auto-deduplicated via set union

#### `tools/hourly_scan.py`
- **BLOCKS_PER_HOUR**: Expanded to all 24 chains with accurate block times
- **discover_new_tokens_on_chain()**: Complete rewrite to 5-level cascade:
  1. RPC event logs (real-time on-chain data)
  2. CoinGecko API (massive token list)
  3. DexScreener (newly boosted/trending)
  4. Ethereum local DB (1.45M pre-collected addresses)
  5. Explorer API (top verified contracts)
- Each strategy independently tries the next on failure

### Next Steps For Future Sessions
1. Actually trigger a scan on all 24 chains (GitHub Actions) to populate full registry
2. Add subgraph/Uniswap pair discovery (TheGraph API)
3. Implement multi-file contract support with AST parsing
4. Add Slither integration for deeper static analysis
5. Add real-time alerting (Telegram/Discord webhooks)

---

*Last updated: 2026-06-18 — Session 2 complete*
