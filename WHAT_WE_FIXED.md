# 👁️⚖️ MaatEye — What We Fixed

This document tracks all the critical bugs, logic errors, and CI/CD conflicts that have been successfully resolved during development.

---

### 1. The Rate Limit Bug (Thread Overload)
- **Bug:** `multichain.py` and `etherscan.py` were using basic floats to track the `_last_request_time`. Because the scanner runs `--workers 10` (10 parallel threads), multiple threads were reading the timestamp simultaneously, bypassing the 5 req/sec rate limit and causing Etherscan to return `HTTP 429 Too Many Requests`.
- **Fix:** Implemented `threading.Lock()` across all fetchers to force parallel threads to cleanly queue up.

### 2. GitHub Pages Deployment Conflict
- **Bug:** The GitHub Actions workflow `web-deploy.yml` was using `actions/deploy-pages@v4` which completely broke the website deployments because the repository was simultaneously configured to deploy natively from the `/docs` branch. 
- **Fix:** Deleted the conflicting `web-deploy.yml` and configured Actions to only output to `docs/dashboard.json`, allowing GitHub to auto-deploy natively.

### 3. Dashboard Overwrite Bug
- **Bug:** The daily scan in `scan-scheduled.yml` was running `generate_dashboard.py`, which would completely overwrite the beautiful custom `docs/index.html` with a basic, ugly HTML template.
- **Fix:** Created `update_dashboard.py` to strictly update the underlying `dashboard.json` data file while leaving the HTML alone. 

### 4. Duplicate Dataclass Fields (Engine Crash)
- **Bug:** `ScanResults` in `scanner/engine.py` had 5 fields duplicated in its declaration, causing runtime initialization errors.
- **Fix:** Cleaned up the dataclass definition.

### 5. Incorrect Method Signature (Pattern Application)
- **Bug:** `_apply_pattern` in `engine.py` was defined as a standalone function but called as an instance method, causing a `self` argument crash at runtime.
- **Fix:** Added `self` and `result: ContractResult` to the method signature.

### 6. Missing Hourly Scan Orchestration
- **Bug:** The scanner only had a daily schedule and no capability to continuously discover and scan new tokens in real-time.
- **Fix:** Wrote `tools/hourly_scan.py` and `.github/workflows/rpc-hourly-scan.yml` to run a 4-phase discovery (eth_getLogs) -> registry dedup -> scan -> dashboard update every hour.
