"""
🦙 MaatEye — DeFiLlama Token Discovery (Source 6)
Discovers tokens via DeFiLlama's comprehensive coin listing API.
DeFiLlama tracks more tokens across more chains than CoinGecko,
especially for newer/L2 chains, with frequent updates.

API: https://coins.llama.fi (free, no API key required)
Endpoints used:
  - /list          — all known coins with chain:address format
  - /prices/current/{chain}:{address} — price + metadata enrichment

Harmless: READ-ONLY — HTTP GET requests to DeFiLlama API only.
"""

import json
import time
import re
from typing import Optional
from urllib.request import urlopen, Request

from scanner.utils.logger import get_logger

logger = get_logger(__name__)

LLAMA_BASE = "https://coins.llama.fi"

DEFAULT_MAX_PER_CHAIN = 2000
_REQUEST_INTERVAL = 0.3  # 300ms between calls

# Map DeFiLlama chain IDs → MaatEye chain keys
# DeFiLlama uses lowercase chain names in the format "chain:address"
LLAMA_CHAIN_MAP: dict[str, str] = {
    "ethereum":  "ethereum",
    "bsc":       "bnb",
    "binance":   "bnb",
    "polygon":   "polygon",
    "arbitrum":  "arbitrum",
    "optimism":  "optimism",
    "base":      "base",
    "avalanche": "avalanche",
    "linea":     "linea",
    "scroll":    "scroll",
    "blast":     "blast",
    "gnosis":    "gnosis",
    "xdai":      "gnosis",
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
    "polygonzkevm": "polygon",
    "zksync":    "ethereum",  # zksync-era → mapped as ethereum-adjacent
}


def _fetch_json(url: str, timeout: int = 30) -> Optional[dict]:
    """Fetch JSON from a URL with User-Agent header."""
    try:
        req = Request(url, headers={
            "User-Agent": "MaatEye/1.0",
            "Accept": "application/json",
        })
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        logger.debug(f"  ⚠️ DeFiLlama fetch failed: {e}")
        return None


def _validate_address(addr: str) -> bool:
    """Validate an EVM contract address."""
    return bool(addr and isinstance(addr, str) and
                re.match(r"^0x[a-fA-F0-9]{40}$", addr))


def discover_from_defillama(
    max_per_chain: int = DEFAULT_MAX_PER_CHAIN,
) -> dict[str, set[str]]:
    """
    Discover token addresses from DeFiLlama's coin list.

    DeFiLlama's /list endpoint returns ALL coins it tracks in the format:
      "ethereum:0xdAC17F958D2ee523a2206206994597C13D831ec7": {
        "symbol": "USDT",
        "name": "Tether",
        "decimals": 6
      }

    This is one of the most comprehensive free token lists available.

    Args:
        max_per_chain: Maximum tokens to return per chain

    Returns:
        Dict of {chain_key: set(addresses)}
    """
    url = f"{LLAMA_BASE}/list"
    data = _fetch_json(url)

    if not data:
        logger.warning("  ⚠️ No data from DeFiLlama coin list")
        return {}

    coins = data if isinstance(data, dict) else {}
    # If wrapped in a "coins" key
    if "coins" in coins:
        coins = coins["coins"]

    result: dict[str, set[str]] = {}
    count_total = 0
    count_mapped = 0
    count_unknown_chain = 0

    for coin_id, info in coins.items():
        count_total += 1

        # coin_id format: "chain:address"
        if ":" not in coin_id:
            continue

        llama_chain, address = coin_id.split(":", 1)

        if not _validate_address(address):
            continue

        maat_key = LLAMA_CHAIN_MAP.get(llama_chain)
        if not maat_key:
            count_unknown_chain += 1
            continue

        address = address.lower()
        if maat_key not in result:
            result[maat_key] = set()
        result[maat_key].add(address)
        count_mapped += 1

    # Limit per chain
    for chain_key in list(result.keys()):
        tokens = result[chain_key]
        if len(tokens) > max_per_chain:
            result[chain_key] = set(sorted(tokens)[:max_per_chain])

    total = sum(len(v) for v in result.values())
    logger.info(f"  ✅ DeFiLlama: {count_mapped} mapped tokens across "
                f"{len(result)} chains (from {count_total} total entries)")
    if count_unknown_chain > 0:
        logger.debug(f"    ({count_unknown_chain} entries skipped — "
                     f"unknown/unmapped chains)")
    for chain, tokens in sorted(result.items()):
        logger.debug(f"    {chain}: {len(tokens)} tokens")

    time.sleep(_REQUEST_INTERVAL)
    return result


if __name__ == "__main__":
    result = discover_from_defillama(max_per_chain=500)
    print(f"\nDeFiLlama found tokens on {len(result)} chains")
    for k, v in sorted(result.items()):
        print(f"  {k}: {len(v)}")
    total = sum(len(v) for v in result.values())
    print(f"Total: {total}")
