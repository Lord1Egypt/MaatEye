"""
🌐 MaatEye — RPC Event-Log Token Discovery
Discovers token contracts by scanning Transfer events from the chain's RPC.
Harmless: READ-ONLY — eth_call and eth_getLogs only, never sends tx.
"""

import json
import time
from dataclasses import dataclass, field
from typing import Optional
from urllib.request import Request, urlopen

from scanner.utils.logger import get_logger

logger = get_logger(__name__)

# ── Transfer Event Topic ──────────────────────────────────────────────────
# keccak256("Transfer(address,address,uint256)")
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

# ── ERC20 Function Selectors ─────────────────────────────────────────────
SELECTOR_SYMBOL = "0x95d89b41"   # symbol()
SELECTOR_NAME = "0x06fdde03"     # name()
SELECTOR_DECIMALS = "0x313ce567"  # decimals()
SELECTOR_TOTAL_SUPPLY = "0x18160ddd"  # totalSupply()

# RPCs known to support eth_getLogs (permissive)
PERMISSIVE_RPCS = {
    "ethereum": [
        "https://ethereum-rpc.publicnode.com",
        "https://rpc.ankr.com/eth",
        "https://eth.merkle.io",
    ],
    "bnb": [
        "https://bsc-dataseed1.binance.org",
        "https://bsc-dataseed2.binance.org",
        "https://bsc-dataseed3.binance.org",
    ],
    "polygon": [
        "https://polygon-rpc.com",
        "https://rpc.ankr.com/polygon",
        "https://polygon.llamarpc.com",
    ],
    "arbitrum": [
        "https://arbitrum.llamarpc.com",
        "https://rpc.ankr.com/arbitrum",
    ],
    "optimism": [
        "https://optimism.llamarpc.com",
        "https://rpc.ankr.com/optimism",
    ],
    "base": ["https://base.llamarpc.com", "https://rpc.ankr.com/base"],
    "avalanche": ["https://avalanche.llamarpc.com", "https://rpc.ankr.com/avalanche"],
}

# RPCs that are archive nodes (can query historical logs)
ARCHIVE_RPCS = {
    "ethereum": ["https://eth.merkle.io"],
    "bnb": [],
    "polygon": [],
}


@dataclass
class TokenInfo:
    """Minimal token information."""
    address: str
    chain: str
    symbol: str = ""
    name: str = ""
    decimals: int = 18
    discovered_at_block: int = 0
    source: str = "rpc_event_log"  # rpc_event_log, coingecko, explorer, subgraph


def _rpc_call(rpc_url: str, method: str, params: list, timeout: int = 30) -> Optional[dict]:
    """Make a JSON-RPC call."""
    payload = json.dumps({
        "jsonrpc": "2.0", "id": 1,
        "method": method,
        "params": params,
    }).encode()

    req = Request(rpc_url, data=payload, headers={
        "Content-Type": "application/json",
        "User-Agent": "MaatEye/1.0",
    })

    try:
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        logger.debug(f"  ⚠️ RPC call failed ({method}): {e}")
        return None


def _safe_decode_hex_string(hex_str: str) -> str:
    """Safely decode a hex-encoded UTF-8 string from eth_call response."""
    if not hex_str or hex_str == "0x" or hex_str == "0x0":
        return ""
    try:
        raw = bytes.fromhex(hex_str[2:])
        # Decode, stripping padding zeros
        return raw.decode("utf-8", errors="replace").strip("\x00").strip()
    except Exception:
        return ""


def get_token_metadata(address: str, rpc_url: str) -> dict:
    """Fetch token metadata (symbol, name, decimals) via eth_call."""
    meta = {"symbol": "", "name": "", "decimals": 18}

    # Get symbol
    result = _rpc_call(rpc_url, "eth_call", [
        {"to": address, "data": SELECTOR_SYMBOL}, "latest"
    ])
    if result and result.get("result"):
        meta["symbol"] = _safe_decode_hex_string(result["result"])

    # Get name
    result = _rpc_call(rpc_url, "eth_call", [
        {"to": address, "data": SELECTOR_NAME}, "latest"
    ])
    if result and result.get("result"):
        meta["name"] = _safe_decode_hex_string(result["result"])

    # Get decimals
    result = _rpc_call(rpc_url, "eth_call", [
        {"to": address, "data": SELECTOR_DECIMALS}, "latest"
    ])
    if result and result.get("result"):
        try:
            meta["decimals"] = int(result["result"], 16)
        except ValueError:
            pass

    return meta


def discover_tokens_via_rpc(
    rpc_url: str,
    from_block: int,
    to_block: int,
    batch_size: int = 500,
) -> set[str]:
    """
    Discover token contract addresses by scanning Transfer event logs.
    
    Uses eth_getLogs to find all Transfer events in a block range and
    extracts unique contract addresses.
    
    Args:
        rpc_url: RPC endpoint URL
        from_block: Starting block number
        to_block: Ending block number
        batch_size: Max blocks per query (to avoid 'limit exceeded' errors)
        
    Returns:
        Set of unique token contract addresses
    """
    tokens: set[str] = set()

    # Process in batches to respect RPC limits
    current_from = from_block
    while current_from < to_block:
        current_to = min(current_from + batch_size, to_block)
        
        params = [{
            "fromBlock": hex(current_from),
            "toBlock": hex(current_to),
            "topics": [TRANSFER_TOPIC],
        }]
        
        result = _rpc_call(rpc_url, "eth_getLogs", params, timeout=60)
        if not result:
            logger.warning(f"  ⚠️ RPC returned no data for blocks {current_from}-{current_to}")
            current_from = current_to
            time.sleep(0.5)
            continue
        
        if "error" in result:
            error_msg = result["error"].get("message", "")
            if "limit" in error_msg.lower() or "too many" in error_msg.lower():
                if batch_size <= 10:
                    logger.warning(f"  ⚠️ RPC rate limit persists at minimum batch size. Skipping to next chunk.")
                    current_from = current_to
                    continue
                # Reduce batch size and retry
                batch_size = max(batch_size // 2, 10)
                logger.debug(f"  📉 Reducing batch to {batch_size} due to rate limit")
                continue
            else:
                logger.warning(f"  ⚠️ RPC error: {error_msg}")
                current_from = current_to
                continue
        
        logs = result.get("result", [])
        for log in logs:
            addr = log.get("address", "").lower()
            if addr and len(addr) == 42 and addr.startswith("0x"):
                tokens.add(addr)
        
        logger.debug(f"  📍 Blocks {current_from}-{current_to}: {len(logs)} events, "
                     f"{len(tokens)} unique tokens so far")
        
        current_from = current_to
        time.sleep(0.2)  # Be nice to the RPC
    
    return tokens


def discover_tokens_rpc_catchup(
    chain_key: str,
    lookback_blocks: int = 50000,
    rpc_urls: Optional[list[str]] = None,
) -> dict[str, TokenInfo]:
    """
    Discover tokens by scanning recent blocks on a chain.
    Designed for initial bulk discovery.
    
    Args:
        chain_key: Chain identifier
        lookback_blocks: How many blocks to scan back
        rpc_urls: Override RPC URLs
        
    Returns:
        Dict of {address: TokenInfo}
    """
    permissive = PERMISSIVE_RPCS.get(chain_key, [])
    urls = rpc_urls or permissive
    
    if not urls:
        logger.warning(f"  ⚠️ No permissive RPCs for {chain_key}")
        return {}
    
    rpc_url = urls[0]
    logger.info(f"  🔍 RPC event-log discovery on {chain_key} "
                f"(scanning {lookback_blocks} blocks back)...")
    
    # Get latest block
    result = _rpc_call(rpc_url, "eth_blockNumber", [])
    if not result or "result" not in result:
        logger.warning(f"  ⚠️ Cannot get block number from {rpc_url}")
        return {}
    
    latest = int(result["result"], 16)
    from_block = max(latest - lookback_blocks, 0)
    
    logger.info(f"  📊 Scanning blocks {from_block} → {latest} "
                f"({lookback_blocks} blocks, ~{lookback_blocks*3 // 60} min of data)")
    
    # Discover token addresses
    addresses = discover_tokens_via_rpc(rpc_url, from_block, latest)
    
    if not addresses:
        logger.warning(f"  ⚠️ No tokens found via RPC on {chain_key}")
        return {}
    
    # Get metadata for a sample
    tokens = {}
    logger.info(f"  🎯 Found {len(addresses)} unique token addresses via RPC")
    
    # For initial discovery, just store addresses (metadata fetched lazily)
    for addr in sorted(addresses):
        tokens[addr] = TokenInfo(
            address=addr,
            chain=chain_key,
            discovered_at_block=latest,
            source="rpc_event_log",
        )
    
    return tokens


def discover_tokens_rpc_all_chains(
    lookback_blocks: int = 50000,
    chains: Optional[list[str]] = None,
) -> dict[str, dict[str, TokenInfo]]:
    """
    Discover tokens via RPC across all supported chains.
    
    Returns:
        Dict of {chain_key: {address: TokenInfo}}
    """
    if chains is None:
        chains = list(PERMISSIVE_RPCS.keys())
    
    results = {}
    for chain_key in chains:
        tokens = discover_tokens_rpc_catchup(chain_key, lookback_blocks)
        if tokens:
            results[chain_key] = tokens
            logger.info(f"  ✅ {chain_key}: {len(tokens)} tokens discovered via RPC")
    
    return results


if __name__ == "__main__":
    # Quick test
    import sys
    chain = sys.argv[1] if len(sys.argv) > 1 else "bnb"
    blocks = int(sys.argv[2]) if len(sys.argv) > 2 else 10000
    
    tokens = discover_tokens_rpc_catchup(chain, lookback_blocks=blocks)
    print(f"\n{'='*50}")
    print(f"Discovered {len(tokens)} tokens on {chain} via RPC event logs")
    print(f"{'='*50}")
    
    if tokens:
        # Get metadata for first 5
        permissive = PERMISSIVE_RPCS.get(chain, [])
        if permissive:
            rpc = permissive[0]
            for addr in list(tokens.keys())[:5]:
                meta = get_token_metadata(addr, rpc)
                print(f"  {addr[:10]}...{addr[-6:]} → "
                      f"{meta.get('symbol', '?')} ({meta.get('name', '?')})")
