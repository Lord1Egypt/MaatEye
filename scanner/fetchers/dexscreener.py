"""
🦎 MaatEye — DexScreener Token Discovery (Source 5)
Discovers newly active/boosted tokens via DexScreener's free public API.
Catches tokens before they appear on CoinGecko — especially useful for
new launches, memecoins, and low-cap tokens on newer chains.

DexScreener chain IDs are mapped to MaatEye internal chain keys.

API: https://api.dexscreener.com (free, no API key required)
Endpoints used:
  - /token-boosts/latest/v1    — newly boosted tokens (real-time)
  - /token-boosts/top/v1       — top boosted tokens
  - /latest/dex/tokens/{addr}  — token details (enrichment)

Harmless: READ-ONLY — HTTP GET requests to DexScreener API only.
"""

import json
import time
import re
from typing import Optional
from urllib.request import urlopen, Request

from scanner.utils.logger import get_logger

logger = get_logger(__name__)

DEXSCREENER_BASE = "https://api.dexscreener.com"

DEFAULT_MAX_PER_CHAIN = 100
_REQUEST_INTERVAL = 0.5  # 500ms between calls

# Map DexScreener chain IDs → MaatEye chain keys
DEXSCREENER_CHAIN_MAP: dict[str, str] = {
    "ethereum":  "ethereum",
    "bsc":       "bnb",
    "polygon":   "polygon",
    "arbitrum":  "arbitrum",
    "optimism":  "optimism",
    "base":      "base",
    "avalanche": "avalanche",
    "linea":     "linea",
    "scroll":    "scroll",
    "blast":     "blast",
    "gnosis":    "gnosis",
    "celo":      "celo",
    "moonbeam":  "moonbeam",
    "metis":     "metis",
    "opbnb":     "opbnb",
    "pulsechain": "pulsechain",
    "mantle":    "mantle",
    "taiko":     "taiko",
    "berachain": "berachain",
    "soneium":   "soneium",
    "unichain":  "unichain",
    "fraxtal":   "fraxtal",
    "chiliz":    "chiliz",
    "sonic":     "sonic",
}


def _fetch_json(url: str, timeout: int = 15) -> Optional[dict]:
    """Fetch JSON from a URL with User-Agent header."""
    try:
        req = Request(url, headers={
            "User-Agent": "MaatEye/1.0",
            "Accept": "application/json",
        })
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        logger.debug(f"  ⚠️ DexScreener fetch failed: {e}")
        return None


def get_token_boosts(max_entries: int = 500) -> list[dict]:
    """
    Fetch latest token boosts from DexScreener.
    Token boosts are newly created or trending tokens — this catches
    tokens that may not yet be indexed by CoinGecko or other aggregators.

    Returns list of boost entries, each containing:
      - chainId (str): DexScreener chain ID
      - tokenAddress (str): contract address
      - boostType (str): "NEW" or "BOOST"
      - amount (int): boost amount in USD
    """
    url = f"{DEXSCREENER_BASE}/token-boosts/latest/v1"
    data = _fetch_json(url)

    if not data:
        logger.warning("  ⚠️ No data from DexScreener token boosts")
        return []

    boosts = data if isinstance(data, list) else data.get("data", [])
    if not isinstance(boosts, list):
        boosts = []

    logger.debug(f"  🦎 DexScreener: {len(boosts)} token boosts fetched")
    return boosts[:max_entries]


def get_top_boosts(max_entries: int = 500) -> list[dict]:
    """
    Fetch top (highest value) token boosts.
    These are tokens with the most real-time liquidity/attention.
    """
    url = f"{DEXSCREENER_BASE}/token-boosts/top/v1"
    data = _fetch_json(url)

    if not data:
        logger.warning("  ⚠️ No data from DexScreener top boosts")
        return []

    boosts = data if isinstance(data, list) else data.get("data", [])
    if not isinstance(boosts, list):
        boosts = []

    logger.debug(f"  🦎 DexScreener: {len(boosts)} top boosts fetched")
    return boosts[:max_entries]


def _validate_address(addr: str) -> bool:
    """Validate an EVM contract address."""
    return bool(addr and isinstance(addr, str) and
                re.match(r"^0x[a-fA-F0-9]{40}$", addr))


def discover_from_dexscreener(
    max_per_chain: int = DEFAULT_MAX_PER_CHAIN,
    include_top_boosts: bool = True,
) -> dict[str, set[str]]:
    """
    Discover token addresses from DexScreener boosts.

    Strategy:
      1. Fetch latest token boosts (newly boosted tokens)
      2. Optionally fetch top boosts (highest-value boosts)
      3. Group by chain, deduplicate, validate addresses
      4. Respect max_per_chain limit

    Args:
        max_per_chain: Maximum tokens to return per chain
        include_top_boosts: Also fetch top boosts (more coverage)

    Returns:
        Dict of {chain_key: set(addresses)}
    """
    result: dict[str, set[str]] = {}

    # Step 1: fetch latest boosts
    all_boosts = get_token_boosts(max_entries=max_per_chain * 4)

    # Step 2: optionally fetch top boosts too
    if include_top_boosts:
        top_boosts = get_top_boosts(max_entries=max_per_chain * 2)
        existing_urls = {b.get("url", "") for b in all_boosts}
        for b in top_boosts:
            if b.get("url", "") not in existing_urls:
                all_boosts.append(b)
                existing_urls.add(b.get("url", ""))

    time.sleep(_REQUEST_INTERVAL)

    # Step 3: group by chain
    for boost in all_boosts:
        chain_id = boost.get("chainId", "")
        token_addr = boost.get("tokenAddress", "")

        maat_key = DEXSCREENER_CHAIN_MAP.get(chain_id)
        if not maat_key:
            continue

        if not _validate_address(token_addr):
            continue

        token_addr = token_addr.lower()

        if maat_key not in result:
            result[maat_key] = set()
        result[maat_key].add(token_addr)

    # Step 4: limit per chain
    for chain_key in list(result.keys()):
        tokens = result[chain_key]
        if len(tokens) > max_per_chain:
            result[chain_key] = set(sorted(tokens)[:max_per_chain])

    total = sum(len(v) for v in result.values())
    logger.info(f"  ✅ DexScreener: {total} tokens across {len(result)} chains")
    for chain, tokens in sorted(result.items()):
        logger.debug(f"    {chain}: {len(tokens)} tokens")

    return result


if __name__ == "__main__":
    result = discover_from_dexscreener()
    print(f"\nDexScreener found tokens on {len(result)} chains")
    for k, v in sorted(result.items()):
        print(f"  {k}: {len(v)}")
    total = sum(len(v) for v in result.values())
    print(f"Total: {total}")
