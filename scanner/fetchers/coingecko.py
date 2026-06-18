"""MaatEye — CoinGecko Fetcher
Fetches top token contract addresses from CoinGecko API.
"""

import json
from typing import Optional
from urllib.request import urlopen, Request

from scanner.utils.logger import get_logger

logger = get_logger(__name__)


def fetch_top_tokens(count: int = 20, network: str = "ethereum") -> list[str]:
    """Fetch top token contract addresses from CoinGecko."""
    addresses = []

    try:
        url = (
            f"https://api.coingecko.com/api/v3/coins/markets"
            f"?vs_currency=usd&order=market_cap_desc"
            f"&per_page={min(count, 250)}&page=1"
            f"&sparkline=false"
        )

        req = Request(url, headers={"User-Agent": "MaatEye/1.0", "Accept": "application/json"})
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        for coin in data:
            if "platforms" in coin:
                addr = coin["platforms"].get(network, "")
                if addr and addr != "" and addr != "-":
                    addresses.append(addr.lower())
                    if len(addresses) >= count:
                        break

        logger.debug(f"🌐 Fetched {len(addresses)} token addresses from CoinGecko")

    except Exception as e:
        logger.warning(f"⚠️ CoinGecko fetch failed: {e}")

    return addresses
