#!/usr/bin/env python3
"""One-off: re-scan existing registry tokens with the fixed engine.

The historical registry was populated by a buggy scanner (dependency files +
comments scanned, 4 patterns crashing, no dedup), so its vuln_counts are
inflated and verified_source was never set. This re-scans the given chain's
existing tokens with the corrected engine and persists accurate results.

Usage: python tools/backfill_rescan.py <chain> [limit]
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scanner.engine import ScanEngine
from scanner.fetchers.token_store import get_store


def rescan_one(store, chain: str, limit: int = 0) -> None:
    tokens = list(store.tokens.get(chain, {}).keys())
    if limit:
        tokens = tokens[:limit]
    print(f"🔁 Re-scanning {len(tokens)} {chain} tokens with fixed engine...", flush=True)

    eng = ScanEngine(chain_key=chain, max_workers=4)
    t0 = time.time()
    done = 0
    old_total = new_total = verified = 0

    for addr in tokens:
        old = store.tokens[chain][addr].vuln_count
        try:
            res = eng._scan_single(addr)
        except Exception as e:  # never let one bad contract abort the backfill
            print(f"  ⚠️ {addr}: {e}", flush=True)
            continue
        if res.error:
            continue
        old_total += old
        new_total += res.vuln_count
        if res.has_verified_source:
            verified += 1
        # Reuse the shared upsert (single-contract results object).
        class _R:
            contracts = {addr: res}
        store.apply_scan_results(_R(), source=f"backfill_{chain}")
        done += 1
        if done % 25 == 0:
            store.save()
            print(f"  …{done}/{len(tokens)}  ({time.time()-t0:.0f}s)  "
                  f"old_sum={old_total} new_sum={new_total} verified={verified}", flush=True)

    store.save()
    print(f"✅ {chain}: re-scanned {done} tokens in {time.time()-t0:.0f}s | "
          f"vuln {old_total}->{new_total} | verified-source: {verified}", flush=True)


def main():
    chain = sys.argv[1] if len(sys.argv) > 1 else "avalanche"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    store = get_store()
    if chain == "all":
        # Avalanche is keyless and already backfilled; do the rest first.
        chains = [c for c in store.tokens if c != "avalanche"] + ["avalanche"]
        for c in chains:
            rescan_one(store, c, limit)
    else:
        rescan_one(store, chain, limit)


if __name__ == "__main__":
    main()
