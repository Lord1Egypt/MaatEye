# 🗺️ MaatEye Roadmap

> *"The Eye of Ma'at sees all — nothing escapes the feather of truth."*

---

## ✅ v0.1 — Foundation

- [x] Core 20 Plagues patterns (P01-P20)
- [x] CI/CD with GitHub Actions
- [x] Pattern submission via Issues
- [x] Community contribution templates

## ✅ v0.2 — Multi-Chain Engine

- [x] **24 EVM chains** (Ethereum, BNB, Polygon, Arbitrum, etc.)
- [x] Chain registry from rpc-radar-bot
- [x] Multi-chain source fetcher (Etherscan + Blockscout APIs)
- [x] Token discovery per chain (Explorer APIs)
- [x] Chain-aware vulnerability reporting
- [x] Cross-chain scan results with chain context

## ✅ v0.3 — Daily Guardian

- [x] **Daily automated cross-chain scan** (08:00 UTC)
- [x] Per-chain summary reports
- [x] Red Flag issues with chain info
- [x] Cross-chain dashboard
- [x] 350+ tokens scanned daily across 24 chains

---

## 🔄 v0.4 — Mass Token Discovery (🔥 NEW)

### 🎯 Goal: Discover & track ALL tokens, not just top 30

#### Source 1: 🪙 CoinGecko API (PRIMARY)
- **Endpoint:** `api.coingecko.com/api/v3/coins/list?include_platform=true`
- **Coverage:** 15,000+ tokens across 100+ chains
- **Rate limit:** 10-30 calls/min (free tier, no API key)
- **Strategy:** Fetch full list, map CoinGecko platforms → MaatEye chain keys
- **Dedup:** Store all addresses in JSON registry, skip duplicates

#### Source 2: 🧾 RPC Event Logs (SECONDARY)
- **Method:** `eth_getLogs` scanning for `Transfer(address,address,uint256)` events
- **Topic:** `0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef`
- **Coverage:** Any ERC20/ERC721 that emitted a Transfer event
- **RPCs tested:**
  - `bsc-dataseed1.binance.org` — ✅ Works (rate limited, small ranges)
  - `ethereum-rpc.publicnode.com` — ⚠️ Returns 0 logs (filters eth_getLogs)
  - `base-rpc.publicnode.com` — ⚠️ Same, public RPCs block heavy log queries
  - `bsc-dataseed1.binance.org` — ✅ Full logs but "limit exceeded" for large ranges
- **Strategy:** 
  - Scan in small batches (50-500 blocks) to avoid rate limits
  - Use permissive RPCs (archive nodes, dataseeds)
  - Fall back to CoinGecko when RPCs are blocked
  - **Incremental:** Only scan recent blocks for NEW tokens

#### Source 3: 🔭 Explorer APIs (TERTIARY)
- **Coverage:** Top 50 tokens per chain (Etherscan/Blockscout)
- **Best for:** Major chains (Ethereum, BSC, Polygon)
- **Limitation:** Doesn't work for chains without explorer API

#### Source 4: 📚 Known Token Lists (FALLBACK)
- **Coverage:** 10-18 well-known tokens per major chain
- **Purpose:** Seed the registry for chains where other sources fail

### 🗄️ Persistent Token Store
- **Format:** JSON-based (zero external dependencies)
- **Location:** `data/token_registry.json`
- **Dedup key:** `(chain, address)` — guaranteed unique
- **Metadata per token:**
  - `address`, `chain`, `symbol`, `name`, `decimals`
  - `source` (where discovered: coingecko/rpc/explorer/known)
  - `discovered_at` (timestamp)
  - `last_scanned`, `scan_count`
  - `has_source` (verified on explorer)
  - `vuln_count`, `max_severity`, `latest_result_hash`
- **Incremental:** Only NEW tokens are added; existing tokens updated with better metadata

### 📊 Token Registry Commands
```bash
# Import tokens from all sources
python -m scanner.main tokens import --coingecko --rpc

# Show registry stats
python -m scanner.main tokens stats

# List new tokens since last scan
python -m scanner.main tokens new

# Export registry
python -m scanner.main tokens export --format json
```

### 🗓️ Tasks
- [ ] CoinGecko API integration (`discover_from_coingecko()`)
- [ ] RPC event-log scanner with batch support (`rpc_discovery.py`)
- [ ] Persistent token store with dedup (`token_store.py`)
- [ ] `tokens` CLI command (import, stats, new, export)
- [ ] Incremental discovery: only scan for NEW tokens daily
- [ ] Token metadata enrichment (symbol, name, decimals via eth_call)
- [ ] Handle RPC rate limits with exponential backoff
- [ ] Git-tracked token registry (version-controlled)

---

## 🔄 v0.5 — ALL-Token Scanning Pipeline

### 🎯 Goal: Scan ALL discovered tokens, not just top 10

#### Architecture
```
Token Registry (10k+ tokens)
       │
       ▼
Scan Scheduler (daily)
       │
       ├── 🔴 Priority 1: New tokens (never scanned)
       ├── 🟡 Priority 2: Previously vulnerable tokens
       └── 🔵 Priority 3: Stable tokens (re-scanned weekly)
```

#### Optimizations
- **Batch scanning:** 50 contracts per run (respect explorer API limits)
- **Skip unverified:** Contracts without source code = skip (save RPC calls)
- **Change detection:** Only re-scan if bytecode changed (compare codehash)
- **Smart throttling:** Per-chain rate limiting (auto-adjusts)
- **Scan state:** SQLite/JSON tracking what was scanned when

#### Output
- Daily report: "Today we scanned 340 new tokens, found 12 vulnerabilities"
- Weekly report: "Full scan of 15,000 tokens complete, 89 critical vulns"
- Alert: Only for CRITICAL/HIGH severity on NEW vulnerabilities

### 🗓️ Tasks
- [ ] Priority-based scan scheduler (new → vulnerable → stable)
- [ ] Change detection via codehash comparison
- [ ] Batch scanning with configurable parallelism
- [ ] Per-chain rate limit tracking and adjustment
- [ ] Scan state persistence (what was scanned, when, results hash)
- [ ] Daily summary reports (new tokens, new vulns, fixed)

---

## 📅 v0.6 — Deeper Analysis

- [ ] Slither integration for deeper static analysis
- [ ] Mythril integration for symbolic execution
- [ ] Multi-file Solidity project support
- [ ] Constructor argument analysis
- [ ] Upgradeable proxy detection with implementation verification

## 📅 v0.7 — Exploitability Scoring

- [ ] Exploitability matrix (can_drain_funds, requires_owner, is_public)
- [ ] Risk classification (CRITICAL_ACTIVE, CRITICAL_DORMANT, etc.)
- [ ] Public exploit path detection
- [ ] Live vs dead contract detection (is there actual value?)

## 📅 v0.8 — Alerting & Intelligence

- [ ] Telegram/Discord alerts for critical vulns
- [ ] Weekly GitHub issue report (consolidated)
- [ ] Vulnerability timeline tracking
- [ ] Public API for programmatic access

## 📅 v0.9 — Non-EVM Support

- [ ] Solana program scanning
- [ ] Bitcoin script analysis
- [ ] TON contract scanning
- [ ] Starknet/Cairo contract scanning
- [ ] Cross-chain vulnerability correlation engine

## 📅 v1.0 — Community Platform

- [ ] Community pattern marketplace
- [ ] Web dashboard with live charts
- [ ] Contract score/rating system
- [ ] Audit readiness report generator
- [ ] Integration with bug bounty platforms (Immunefi, Hats Finance)

## 📅 v2.0 — Guardian Network

- [ ] Decentralized guardian node network
- [ ] Real-time exploit detection (mempool monitoring)
- [ ] Cross-chain vulnerability correlation
- [ ] DAO-governed pattern registry
- [ ] Machine learning for anomaly detection
- [ ] ZK-proof verification analysis
- [ ] Formal verification integration
- [ ] MEV attack vector detection
- [ ] Cross-chain bridge vulnerability scanner

---

<p align="center">
  <i>حرية فلسطين — فلسطين حرة عربية</i> 🇵🇸
</p>
