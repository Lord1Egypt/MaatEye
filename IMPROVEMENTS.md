# 👁️⚖️ MaatEye — Future Improvements

This document outlines the long-term vision, architectural upgrades, and feature expansions planned for MaatEye.

---

## ✅ Completed Improvements

### 1. Full 24-Chain RPC Event-Log Discovery
- **Before:** `PERMISSIVE_RPCS` in `scanner/fetchers/rpc_discovery.py` only had 7 chains
- **After:** All 24 EVM chains have publicnode.com RPC endpoints for `eth_getLogs` Transfer event scanning
- **Archive support:** Added `ARCHIVE_RPCS` for ethereum, polygon, gnosis, and celo (historical block queries)

### 2. DexScreener Token Discovery (Source 5)
- **Created:** `scanner/fetchers/dexscreener.py`
- **API:** `api.dexscreener.com/token-boosts/latest/v1` (free, no API key)
- **Coverage:** Real-time newly boosted/trending tokens across all chains
- **Catches:** Tokens before CoinGecko lists them (new launches, memecoins, low-cap)

### 3. DeFiLlama Token Discovery (Source 6)
- **Created:** `scanner/fetchers/defillama.py`
- **API:** `coins.llama.fi/list` (free, no API key)
- **Coverage:** Comprehensive multi-chain coin list — broader than CoinGecko for newer chains
- **Scale:** 500K+ coin entries mapped to 24 EVM chains

### 4. Improved Discovery Cascade in Hourly Scanner
- **Before:** Ethereum-only fallback to local 1.45M token DB
- **After:** 5-level discovery cascade for ALL chains: RPC → CoinGecko → DexScreener → Local DB → Explorer API

---

### 1. The 60+ Chain Expansion
- **Current State:** 24 EVM chains explicitly supported in `scanner/chains/`.
- **Improvement:** Expand the chain dictionary to natively support all 60+ blockchains supported by Etherscan V2 API (e.g., Kroma, ZkSync, Scroll, Linea, Blast, etc.).

### 2. Multi-File Contract Support
- **Current State:** The scanner currently merges flattened source code or processes the main contract file.
- **Improvement:** Implement abstract syntax tree (AST) parsing (via tools like Slither integration) to perfectly track data flows across inherited, multi-file smart contracts.

### 3. Proxy & Implementation Analysis
- **Current State:** The scanner fetches the source code of the exact address requested.
- **Improvement:** Add logic to detect EIP-1967 Proxy contracts automatically. When a proxy is detected, the scanner should automatically fetch the source code of the underlying Implementation contract and scan that instead.

### 4. Advanced False-Positive Reduction
- **Current State:** Regex and basic AST matching for vulnerabilities (the 20 Plagues).
- **Improvement:** Implement context-awareness. For example, if the scanner detects an integer overflow (P04), it should automatically check if the contract imports and uses OpenZeppelin's `SafeMath`, or if it is compiled with Solidity >= 0.8.0, and adjust the confidence score accordingly.

### 5. Automated PDF Reports
- **Current State:** Results are pushed to JSON, displayed on GitHub Pages, and reported as GitHub Issues.
- **Improvement:** Generate professional PDF security audit reports for any scanned token, exportable directly from the GitHub Pages dashboard.

### 6. Subgraph Integration (Source 5)
- **Current State:** Tokens are discovered via CoinGecko, manual import, and RPC event logs.
- **Improvement:** Add TheGraph (GraphQL) as a discovery source to automatically pull the top volume pairs from Uniswap V2/V3 forks across all chains.
