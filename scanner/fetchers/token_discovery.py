"""
🌐 MaatEye — Token Discovery Across All EVM Chains
Discovers token contract addresses from multiple sources:
  1. 🪙 CoinGecko API (10,000+ tokens across all chains)
  2. 🧾 RPC Event Logs (eth_getLogs Transfer events)
  3. 🔭 Explorer API top token lists (Etherscan/Blockscout)
  4. 📚 Known token lists (curated defaults)
  5. 🏪 DEX Subgraphs (Uniswap/PancakeSwap pairs)

All methods are READ-ONLY — no transactions, no exploits, no write operations.
"""

import json
import time
from typing import Optional
from urllib.request import urlopen, Request
from urllib.parse import urlencode

from scanner.chains import EVMChain, list_chains
from scanner.utils.logger import get_logger

logger = get_logger(__name__)

# ── CoinGecko API ────────────────────────────────────────────────────────────
# Free tier: 10-30 calls/min, no API key required for /coins/list
COINGECKO_BASE = "https://api.coingecko.com/api/v3"


def discover_from_coingecko(
    chain_map: Optional[dict[str, str]] = None,
) -> dict[str, set[str]]:
    """
    Discover tokens from CoinGecko's massive token list.
    
    CoinGecko tracks 15,000+ tokens across 100+ chains.
    This is the PRIMARY source for broad token discovery.
    
    Chain key mapping (CoinGecko platform → MaatEye key):
        ethereum → ethereum
        binance-smart-chain → bnb
        polygon-pos → polygon
        arbitrum-one → arbitrum
        optimistic-ethereum → optimism
        base → base
        avalanche → avalanche
        etc.
    
    Returns:
        Dict of {chain_key: set(addresses)}
    """
    if chain_map is None:
        chain_map = {
            "ethereum": "ethereum",
            "binance-smart-chain": "bnb",
            "polygon-pos": "polygon",
            "arbitrum-one": "arbitrum",
            "optimistic-ethereum": "optimism",
            "base": "base",
            "avalanche": "avalanche",
            "linea": "linea",
            "scroll": "scroll",
            "blast": "blast",
            "gnosis": "gnosis",
            "celo": "celo",
            "moonbeam": "moonbeam",
            "metis-andromeda": "metis",
            "mantle": "mantle",
            "taiko": "taiko",
            "berachain": "berachain",
            "fraxtal": "fraxtal",
            "chiliz": "chiliz",
            "sonic": "sonic",
            "pulsechain": "pulsechain",
        }
    
    url = f"{COINGECKO_BASE}/coins/list?include_platform=true"
    logger.info(f"🌐 Fetching token list from CoinGecko...")
    
    try:
        req = Request(url, headers={"User-Agent": "MaatEye/1.0", "Accept": "application/json"})
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        logger.warning(f"  ⚠️ CoinGecko API failed: {e}")
        return {}
    
    # Group by chain
    result: dict[str, set[str]] = {}
    for coin in data:
        platforms = coin.get("platforms", {})
        for platform_key, address in platforms.items():
            if not address or not isinstance(address, str):
                continue
            address = address.lower().strip()
            if not address.startswith("0x") or len(address) != 42:
                continue
            
            maat_key = chain_map.get(platform_key)
            if maat_key:
                if maat_key not in result:
                    result[maat_key] = set()
                result[maat_key].add(address)
    
    total = sum(len(v) for v in result.values())
    logger.info(f"  ✅ CoinGecko: {total} tokens across {len(result)} chains")
    for chain, tokens in sorted(result.items()):
        logger.info(f"    {chain}: {len(tokens)} tokens")
    
    return result


# ── Explorer API Token List ──────────────────────────────────────────────────

def discover_from_explorer(
    chain: EVMChain,
    count: int = 50,
    api_key: str = "",
) -> list[str]:
    """
    Discover top tokens from explorer API (Etherscan-compatible).
    Good for finding recently deployed/active tokens.
    """
    if not chain.explorer_api:
        return []
    
    addresses = []
    params = {
        "module": "token",
        "action": "tokenlist",
        "page": 1,
        "offset": min(count, 50),
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
        logger.debug(f"    Explorer token list failed: {e}")
    
    return addresses


# ── Known Token Lists ────────────────────────────────────────────────────────

def get_known_tokens(chain_key: str) -> list[str]:
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
            "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2",  # MKR
            "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",  # AAVE
            "0x853d955aCEf822Db058eb8505911ED77F175b99e",  # FRAX
            "0x5f98805A4E8be255a32880FDeC7F6728C6568bA0",  # LUSD
            "0xD533a949740bb3306d119CC777fa900bA034cd52",  # CRV
            "0xBA12222222228d8Ba445958a75a0704d566BF2C8",  # BAL
            "0x111111111117dC0aa78b770fA6A738034120C302",  # 1INCH
            "0x408e41876cCCDC0F92210600ef50372656052a38",  # REN
        ],
        "bnb": [
            "0x55d398326f99059fF775485246999027B3197955",  # USDT (BSC)
            "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",  # USDC (BSC)
            "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",  # WBNB
            "0x2170Ed0880ac9A755fd29B2688956BD959F933F8",  # WETH (BSC)
            "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",  # BTCB
            "0x1AF3F329e8BE154074D8769D1FFa4eE058B1DBc3",  # DAI (BSC)
            "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",  # CAKE
            "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56",  # BUSD
            "0x3EE2200Efb3400fAbB9AacF31297cBdD1d435D47",  # ADA (BSC)
            "0x7083609fCE4d1d8Dc0C979AAb8c869Ea2C873402",  # DOT (BSC)
            "0xCC42724C6683B7E57334c4E856f4c9965ED682bD",  # MATIC (BSC)
            "0xF8A0BF9cF54Bb92F17374d9e9A321E6a111a51bD",  # LINK (BSC)
            "0x47BEAd2563dCBf3bF2c9407fEa4dC236fAbA485A",  # SXP (BSC)
            "0x1D2F0da169ceB9fC7B3144628dB156f3F6c60dBE",  # XRP (BSC)
            "0x4338665CBB7B2485A8855A139b75D5e34AB0DB94",  # LTC (BSC)
        ],
        "polygon": [
            "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",  # USDC
            "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",  # USDT
            "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",  # WMATIC
            "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063",  # DAI
            "0x1BFd67037B42fC47b8948DbB5Fc537D7dF4b2b6C",  # WBTC
            "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",  # WETH
            "0x9c2C5fd7b07E95EE044DDeba0E97a665F142394f",  # 1INCH
            "0xb33EaAd8d922B1083446DC23f610c2567fB5180f",  # UNI
            "0x53E0bca35eC356BD5ddDFebbD1Fc0fD03FaBad39",  # LINK
            "0xD6DF932A45C0f255f85145f286eA0b292B21C90B",  # AAVE
        ],
        "arbitrum": [
            "0xFD086bc7CD5C481DCC9C85ebE478A1C0b69FCbb9",  # USDT
            "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",  # USDC
            "0x912CE59144191C1204E64559FE8253a0e49E6548",  # ARB
            "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",  # WETH
            "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f",  # WBTC
            "0xFa7F8980b0f1E64A2062791cc3b0871572f1F7f0",  # UNI
            "0xf97f4df75117a78c1A5a0DBb814Af92458539FB4",  # LINK
            "0xba5DdD1f9d7F570dc94a51479a000E3BCE967196",  # AAVE
            "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1",  # DAI
            "0x17FC002b466eEc40DaE837Fc4bE5c67993ddBd6F",  # FRAX
        ],
        "optimism": [
            "0x7F5c764cBc14f9669B88837ca1490cCa17c31607",  # USDC
            "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58",  # USDT
            "0x4200000000000000000000000000000000000006",  # WETH
            "0x4200000000000000000000000000000000000042",  # OP
            "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1",  # DAI
            "0x68f180fcCe6836688e9084f035309E29Bf0A2095",  # WBTC
            "0x350a791Bfc2C21F9Ed5d10980Dad2e2638ffa7f6",  # LINK
            "0x76FB31fb4af56892A25e32cFC43De717950c9278",  # AAVE
        ],
        "base": [
            "0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA",  # USDbC
            "0x4200000000000000000000000000000000000006",  # WETH
            "0x4ed4E862860beD51a9570b96d89aF5E1B0Efefed",  # DEGEN
            "0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22",  # cbETH
            "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",  # DAI
            "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # USDC
        ],
        "avalanche": [
            "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",  # USDC
            "0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7",  # USDT
            "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",  # WAVAX
            "0x49D5c2BdFfac6CE2BFdB6640F4F80f226bc10bAB",  # WETH
            "0xd586E7F844cEa2F87f50152665BCbc2C279D8d70",  # DAI
            "0x50b7545627a5162F82A992c33b87aDc75187B218",  # WBTC
            "0x5947BB275c521040051D82396192181b413227A3",  # LINK
            "0x63a72806098Bd3D9520cC43356dD78afe5D386D9",  # AAVE
            "0x152b9d0FdC40C096757F570A51E5bd6dA2b0B1a3",  # QI
        ],
    }
    
    return KNOWN_TOKENS.get(chain_key, [])


# ── Master Discovery Orchestrator ────────────────────────────────────────────

def discover_all_tokens(
    use_coingecko: bool = True,
    use_rpc: bool = True,
    use_explorer: bool = True,
    use_known: bool = True,
    tokens_per_chain_explorer: int = 50,
) -> dict[str, set[str]]:
    """
    Master token discovery — aggregates from ALL sources.
    
    Strategy:
    1. CoinGecko API (massive list, 10k+ tokens)
    2. RPC event log scanning (real on-chain activity)
    3. Explorer API top lists
    4. Known/curated token lists
    
    All results are deduplicated automatically.
    
    Returns:
        Dict of {chain_key: set(addresses)}
    """
    master: dict[str, set[str]] = {}
    
    # ── Source 1: CoinGecko ──────────────────────────────────────────────
    if use_coingecko:
        logger.info("🪙  Source 1/4: CoinGecko API (10k+ tokens)...")
        try:
            cg_tokens = discover_from_coingecko()
            for chain, tokens in cg_tokens.items():
                if chain not in master:
                    master[chain] = set()
                master[chain].update(tokens)
            logger.info(f"  ✅ CoinGecko: {sum(len(v) for v in cg_tokens.values())} tokens")
        except Exception as e:
            logger.warning(f"  ⚠️ CoinGecko failed: {e}")
    
    # ── Source 2: RPC Event Logs ─────────────────────────────────────────
    if use_rpc:
        logger.info("🧾  Source 2/4: RPC Event Logs (on-chain Transfer events)...")
        from scanner.fetchers.rpc_discovery import discover_tokens_rpc_all_chains
        try:
            rpc_tokens = discover_tokens_rpc_all_chains(lookback_blocks=20000)
            for chain, tokens in rpc_tokens.items():
                if chain not in master:
                    master[chain] = set()
                master[chain].update(tokens.keys())
            logger.info(f"  ✅ RPC: {sum(len(v) for v in rpc_tokens.values())} tokens")
        except Exception as e:
            logger.warning(f"  ⚠️ RPC discovery failed: {e}")
    
    # ── Source 3: Explorer API ───────────────────────────────────────────
    if use_explorer:
        logger.info("🔭  Source 3/4: Explorer API top token lists...")
        chains = list_chains()
        for chain in chains:
            try:
                tokens = discover_from_explorer(chain, count=tokens_per_chain_explorer)
                if tokens:
                    if chain.key not in master:
                        master[chain.key] = set()
                    master[chain.key].update(tokens)
            except Exception as e:
                logger.debug(f"  ⚠️ Explorer failed for {chain.name}: {e}")
    
    # ── Source 4: Known Tokens ───────────────────────────────────────────
    if use_known:
        logger.info("📚  Source 4/4: Known/curated token lists...")
        for chain_key in list_chains():
            tokens = get_known_tokens(chain_key.key)
            if tokens:
                if chain_key.key not in master:
                    master[chain_key.key] = set()
                master[chain_key.key].update(t.lower() for t in tokens)
    
    # Final summary
    total = sum(len(v) for v in master.values())
    logger.info(f"\n{'='*50}")
    logger.info(f"🏆  TOKEN DISCOVERY COMPLETE")
    logger.info(f"{'='*50}")
    logger.info(f"Total tokens: {total}")
    logger.info(f"Total chains: {len(master)}")
    for chain, tokens in sorted(master.items()):
        logger.info(f"  {chain:<12}: {len(tokens):>6} tokens")
    
    return master


def discover_top_tokens(
    chain: EVMChain,
    count: int = 20,
    api_key: str = "",
) -> list[str]:
    """
    Legacy: discover top tokens on a single chain.
    Falls back through: Explorer → Known tokens → empty.
    """
    addresses = []
    
    # Strategy 1: Explorer API
    try:
        api_addrs = discover_from_explorer(chain, count, api_key)
        addresses.extend(api_addrs)
    except Exception:
        pass
    
    # Strategy 2: Known tokens
    known = get_known_tokens(chain.key)
    for addr in known:
        if addr.lower() not in {a.lower() for a in addresses}:
            addresses.append(addr.lower())
    
    # Deduplicate
    seen = set()
    unique = []
    for addr in addresses:
        a = addr.lower().strip()
        if a not in seen and len(a) == 42 and a.startswith("0x"):
            seen.add(a)
            unique.append(a)
    
    return unique[:count]


def discover_all_chains(
    chains: Optional[list[EVMChain]] = None,
    tokens_per_chain: int = 10,
) -> dict[str, list[str]]:
    """Legacy: discover tokens across all chains via explorer + known lists."""
    if chains is None:
        chains = list_chains()
    
    result = {}
    for chain in chains:
        logger.info(f"🔍 Discovering tokens on {chain.name}...")
        tokens = discover_top_tokens(chain, count=tokens_per_chain)
        result[chain.key] = tokens
    
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "coingecko":
        result = discover_from_coingecko()
        print(f"\nCoinGecko found tokens on {len(result)} chains")
        for k, v in sorted(result.items()):
            print(f"  {k}: {len(v)}")
    else:
        result = discover_all_tokens(use_rpc=False, use_coingecko=True)
        print(f"\nTotal: {sum(len(v) for v in result.values())} tokens")
