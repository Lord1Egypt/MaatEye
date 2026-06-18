"""
🌐 MaatEye — Token Discovery Across All EVM Chains
Discovers popular token addresses on each chain for scanning.
Harmless: READ-ONLY — queries explorer APIs for top token lists.
"""

import json
import time
from typing import Optional
from urllib.request import urlopen, Request
from urllib.parse import urlencode

from scanner.chains import EVMChain, list_chains
from scanner.utils.logger import get_logger

logger = get_logger(__name__)


def discover_top_tokens(
    chain: EVMChain,
    count: int = 20,
    api_key: str = "",
) -> list[str]:
    """
    Discover top token contract addresses on a chain.
    
    Strategy (tried in order):
    1. Explorer token list API (Etherscan-compatible)
    2. Known token lists (from CoinGecko / default lists)
    3. Fallback to popular token addresses
    
    Returns:
        List of contract addresses (lowercase 0x...)
    """
    addresses = []

    # Strategy 1: Explorer API top tokens
    try:
        api_addrs = _fetch_from_explorer(chain, count, api_key)
        addresses.extend(api_addrs)
    except Exception as e:
        logger.debug(f"  ⚠️ Explorer token list failed for {chain.name}: {e}")

    # Strategy 2: Well-known tokens for this chain
    known = _get_known_tokens(chain.key)
    for addr in known:
        if addr.lower() not in {a.lower() for a in addresses}:
            addresses.append(addr.lower())

    # Deduplicate and limit
    seen = set()
    unique = []
    for addr in addresses:
        a = addr.lower().strip()
        if a not in seen and len(a) == 42 and a.startswith("0x"):
            seen.add(a)
            unique.append(a)

    result = unique[:count]
    logger.info(f"  🎯 Discovered {len(result)} tokens on {chain.name}")
    return result


def _fetch_from_explorer(chain: EVMChain, count: int, api_key: str) -> list[str]:
    """Fetch top token addresses from explorer API."""
    if not chain.explorer_api:
        return []

    addresses = []
    page = 1
    per_page = min(count, 50)

    params = {
        "module": "token",
        "action": "tokenlist",
        "page": page,
        "offset": per_page,
        "apikey": api_key or "",
    }

    url = f"{chain.explorer_api}?{urlencode(params)}"

    try:
        req = Request(url, headers={"User-Agent": "MaatEye/1.0"})
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        if data.get("status") == "1":
            for token in data.get("result", []):
                addr = token.get("contractAddress", "") or token.get("address", "")
                if addr and addr != "-":
                    addresses.append(addr.lower())
    except Exception as e:
        logger.debug(f"    Explorer token list: {e}")

    return addresses


def _get_known_tokens(chain_key: str) -> list[str]:
    """Get a curated list of well-known tokens per chain."""
    KNOWN_TOKENS = {
        "ethereum": [
            "0xdAC17F958D2ee523a2206206994597C13D831ec7",  # USDT
            "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
            "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",  # WBTC
            "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
            "0x6B175474E89094C44Da98b954EedeAC495271d0F",  # DAI
            "0x514910771AF9Ca656af840dff83E8264EcF986CA",  # LINK
            "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0",  # MATIC
            "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",  # UNI
            "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",  # SHIB
            "0x3845badAde8e6dFF049820680d1F14bD3903a5d0",  # SAND
        ],
        "bnb": [
            "0x55d398326f99059fF775485246999027B3197955",  # USDT (BSC)
            "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",  # USDC (BSC)
            "0x2170Ed0880ac9A755fd29B2688956BD959F933F8",  # WETH (BSC)
            "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",  # BTCB
            "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",  # WBNB
            "0x1AF3F329e8BE154074D8769D1FFa4eE058B1DBc3",  # DAI (BSC)
            "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",  # CAKE
        ],
        "polygon": [
            "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",  # USDC (Polygon)
            "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",  # USDT (Polygon)
            "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0",  # MATIC
            "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",  # WMATIC
            "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063",  # DAI (Polygon)
            "0x1BFd67037B42fC47b8948DbB5Fc537D7dF4b2b6C",  # WBTC (Polygon)
        ],
        "arbitrum": [
            "0xFD086bc7CD5C481DCC9C85ebE478A1C0b69FCbb9",  # USDT (Arbitrum)
            "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",  # USDC (Arbitrum)
            "0x912CE59144191C1204E64559FE8253a0e49E6548",  # ARB
            "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",  # WETH (Arbitrum)
            "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f",  # WBTC (Arbitrum)
        ],
        "optimism": [
            "0x7F5c764cBc14f9669B88837ca1490cCa17c31607",  # USDC (Optimism)
            "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58",  # USDT (Optimism)
            "0x4200000000000000000000000000000000000006",  # WETH (Optimism)
            "0x4200000000000000000000000000000000000042",  # OP
        ],
        "base": [
            "0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA",  # USDbC (Base)
            "0x4200000000000000000000000000000000000006",  # WETH (Base)
            "0x4ed4E862860beD51a9570b96d89aF5E1B0Efefed",  # DEGEN
        ],
        "avalanche": [
            "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",  # USDC (Avalanche)
            "0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7",  # USDT (Avalanche)
            "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",  # WAVAX
            "0x49D5c2BdFfac6CE2BFdB6640F4F80f226bc10bAB",  # WETH (Avalanche)
        ],
    }

    return KNOWN_TOKENS.get(chain_key, [])


def discover_all_chains(
    chains: Optional[list[EVMChain]] = None,
    tokens_per_chain: int = 10,
) -> dict[str, list[str]]:
    """
    Discover tokens across all EVM chains.
    
    Returns:
        Dict of {chain_key: [addresses]}
    """
    if chains is None:
        chains = list_chains()

    result = {}
    for chain in chains:
        logger.info(f"🔍 Discovering tokens on {chain.name}...")
        tokens = discover_top_tokens(chain, count=tokens_per_chain)
        result[chain.key] = tokens

    total_tokens = sum(len(v) for v in result.values())
    logger.info(f"✅ Discovered {total_tokens} tokens across {len(result)} chains")

    return result
