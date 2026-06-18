"""MaatEye — CoinGecko Fetcher
Fetches top token contract addresses from CoinGecko API.
"""

import json
from typing import Optional
from urllib.request import urlopen, Request

from scanner.utils.logger import get_logger

logger = get_logger(__name__)


import json
from urllib.request import urlopen, Request
from scanner.utils.logger import get_logger

logger = get_logger(__name__)

# Map our internal chain keys to CoinGecko's platform IDs
CG_PLATFORMS = {
    "ethereum": "ethereum",
    "bnb": "binance-smart-chain",
    "polygon": "polygon-pos",
    "arbitrum": "arbitrum-one",
    "optimism": "optimistic-ethereum",
    "base": "base",
    "avalanche": "avalanche",
    "linea": "linea",
    "scroll": "scroll",
    "blast": "blast",
    "celo": "celo",
    "gnosis": "xdai",
    "moonbeam": "moonbeam",
    "metis": "metis-andromeda",
    "mantle": "mantle",
}

# Global cache to avoid hitting the 15MB list repeatedly in one run
_cg_cache = None

def get_coingecko_tokens_for_chain(chain_key: str, max_count: int = 2000) -> list[str]:
    """Fetch thousands of token addresses for a specific chain from CoinGecko."""
    global _cg_cache
    
    cg_platform = CG_PLATFORMS.get(chain_key)
    if not cg_platform:
        return []

    if _cg_cache is None:
        try:
            logger.info("  🦎 Fetching massive token list from CoinGecko (takes a few seconds)...")
            url = "https://api.coingecko.com/api/v3/coins/list?include_platform=true"
            req = Request(url, headers={"User-Agent": "MaatEye/1.0", "Accept": "application/json"})
            with urlopen(req, timeout=30) as resp:
                _cg_cache = json.loads(resp.read().decode())
        except Exception as e:
            logger.warning(f"  ⚠️ CoinGecko fetch failed: {e}")
            _cg_cache = []

    addresses = []
    for coin in _cg_cache:
        platforms = coin.get("platforms", {})
        addr = platforms.get(cg_platform, "")
        if addr and len(addr) == 42 and addr.startswith("0x"):
            addresses.append(addr.lower())
            if len(addresses) >= max_count:
                break

    logger.debug(f"  🦎 Found {len(addresses)} tokens for {chain_key} via CoinGecko")
    return addresses
