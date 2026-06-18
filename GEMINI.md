# MaatEye — AI Assistant Memory (GEMINI.md)

> **Important**: This file provides permanent context, architecture rules, and constraints for any AI coding assistant (Antigravity, Claude, etc.) working on this repository.

## 🏛️ Project Identity
- **Name:** MaatEye (ماعت)
- **Purpose:** Open-source, community-driven smart contract vulnerability scanner.
- **Scope:** 20+ dangerous patterns, 24 EVM chains, 15,000+ tokens.
- **Core Principle:** Harmless execution. READ-ONLY operations only (RPC `eth_getLogs`, `eth_call`, Explorer APIs). No exploits, no transactions.

## 🏗️ Architecture
1. **`scanner/fetchers/`** — Gets code and token lists. 
   - Uses `token_discovery.py` to find tokens via CoinGecko, RPC event logs, etc.
   - Saves persistent state to `data/token_registry.json`.
2. **`scanner/patterns/`** — 20 Plague detection patterns in YAML format.
3. **`scanner/engine.py`** — The `ScanEngine` orchestrates fetching code and applying patterns.
4. **`docs/`** — Contains the live GitHub Pages dashboard. `index.html` fetches `dashboard.json` purely client-side.
5. **`tools/hourly_scan.py`** — The main CLI orchestrator run by GitHub Actions (`.github/workflows/rpc-hourly-scan.yml`).

## ⚠️ Critical Constraints (Zero Tolerance)
- **Do NOT overwrite `docs/index.html`**: It is a carefully crafted Egyptian-themed UI. All data updates MUST go through `docs/dashboard.json` using `tools/update_dashboard.py`.
- **Do NOT use `generate_dashboard.py`**: It is legacy and overwrites the UI.
- **Do NOT use `actions/deploy-pages@v4` in Actions**: This repo uses the native `/docs` folder deployment for GitHub Pages. Custom Pages action workflows will conflict and fail.
- **Always preserve Data**: Updates to `data/token_registry.json` or `docs/dashboard.json` must be *cumulative* merges, not destructive overwrites.

## 🐍 Python Coding Standards
- **Version:** Python 3.11+
- **Typing:** Strict type hints on all function signatures (`def func(arg: str) -> dict:`).
- **Format:** Keep dependencies minimal. Prefer standard library (`urllib.request` over `requests` where possible, though `requests` is allowed if in `requirements.txt`).
- **Error Handling:** Gracefully catch API timeouts. Public RPCs and Explorers *will* rate limit and fail. Never crash the scanner due to an API timeout.

## 🔄 Routine Operations
- To run a manual scan: `python tools/hourly_scan.py --max-new 100 --workers 5`
- To run discovery without scanning: `python tools/hourly_scan.py --no-scan`
- To check current token registry stats: `python -m scanner.main tokens stats`

## 📖 Session Resumption
If continuing previous work, ALWAYS read:
1. `CHECKPOINTS.md` (Logs of all past AI sessions)
2. `DEVELOPMENT_MAP.md` (The 7-Phase roadmap and known issues)
