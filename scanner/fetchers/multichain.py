"""
🌐 MaatEye — Multi-Chain Contract Source Fetcher
Fetches verified contract source code from any EVM chain's explorer.
Supports Etherscan-compatible APIs + Blockscout APIs.
Harmless: READ-ONLY — never sends transactions, never deploys.
"""

import json
import time
from typing import Optional
from urllib.request import urlopen, Request
from urllib.parse import urlencode

from scanner.chains import EVMChain, get_chain, EVM_CHAINS
from scanner.utils.logger import get_logger
from scanner.utils.source_prep import flatten_sources

logger = get_logger(__name__)

import threading
from collections import defaultdict

# In-memory cache: {(chain_key, address): dict}
_source_cache: dict[str, dict] = {}
_last_request_time: dict[str, float] = {}  # Per-chain rate limiting
_rate_limit_locks = defaultdict(threading.Lock)


def fetch_contract_source(
    address: str,
    chain: EVMChain | str,
    api_key: str = "",
) -> Optional[dict]:
    """
    Fetch a verified contract's source code from the chain's explorer.
    
    Args:
        address: Contract address (0x...)
        chain: EVMChain object or chain key string
        api_key: Optional explorer API key
        
    Returns:
        Dict with source_code, contract_name, compiler, etc., or None
    """
    # Resolve chain
    if isinstance(chain, str):
        c = get_chain(chain)
        if not c:
            logger.warning(f"❌ Unknown chain: {chain}")
            return None
        chain_obj = c
    else:
        chain_obj = chain

    cache_key = f"{chain_obj.key}:{address.lower()}"
    
    # Check cache
    if cache_key in _source_cache:
        logger.debug(f"  📦 Cache hit: {address} on {chain_obj.name}")
        return _source_cache[cache_key]

    import os
    from scanner.utils.config import load_config
    
    if not api_key:
        # Check environment variable
        api_key = os.environ.get("ETHERSCAN_API_KEY", "")
        # Fallback to config file
        if not api_key:
            config = load_config()
            api_key = config.get("etherscan", {}).get("api_key", "")

    # Thread-safe rate limiting per chain
    min_interval = 1.0 / chain_obj.scan_limit_rps
    with _rate_limit_locks[chain_obj.key]:
        last = _last_request_time.get(chain_obj.key, 0)
        elapsed = time.time() - last
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        _last_request_time[chain_obj.key] = time.time()

    # Try Etherscan-compatible API first
    result = _try_etherscan_api(address, chain_obj, api_key)
    
    # Fallback: try Blockscout API
    if result is None:
        result = _try_blockscout_api(address, chain_obj)
    
    # Fallback: try direct RPC bytecode check (just to verify it's a contract)
    if result is None:
        result = _try_rpc_bytecode(address, chain_obj)

    if result:
        _source_cache[cache_key] = result
        logger.debug(f"  ✅ Fetched {address} on {chain_obj.name}"
                      f" ({result.get('contract_name', 'Unknown')}, "
                      f"{len(result.get('source_code', ''))} bytes)")
    else:
        logger.debug(f"  ⚠️ No source for {address} on {chain_obj.name}")

    return result


# Etherscan V2 unified API: a single API key works across ~60 chains, selected
# by chainid. The legacy per-chain V1 endpoints (api.basescan.org, …) now
# require a per-chain key and are being deprecated.
ETHERSCAN_V2_API = "https://api.etherscan.io/v2/api"


def _try_etherscan_api(address: str, chain: EVMChain, api_key: str = "") -> Optional[dict]:
    """Try an Etherscan-compatible explorer API for verified source.

    With a key, use the Etherscan **V2 unified** endpoint (one key → all chains
    via chainid) — this is what lets every chain return verified source, not
    just Avalanche. Without a key, fall back to the chain's native V1 endpoint,
    which still works keyless for some explorers (e.g. Snowtrace/Avalanche).
    """
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
    }

    if api_key and getattr(chain, "chain_id", 0):
        url = f"{ETHERSCAN_V2_API}?{urlencode({**params, 'chainid': chain.chain_id, 'apikey': api_key})}"
    elif chain.explorer_api:
        url = f"{chain.explorer_api}?{urlencode({**params, 'apikey': api_key or ''})}"
    else:
        return None

    try:
        req = Request(url, headers={"User-Agent": "MaatEye/1.0"})
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        if data.get("status") != "1":
            return None

        result = data.get("result", [{}])[0]
        source_code = result.get("SourceCode", "")
        if not source_code:
            return None

        # Flatten Solidity Standard-JSON input, including Etherscan's ``{{...}}``
        # double-brace wrapping (plain json.loads fails on it). Keeps the
        # project's own files, drops bundled third-party libraries.
        flat, _ = flatten_sources(source_code)
        if flat:
            source_code = flat

        return {
            "address": address,
            "chain": chain.key,
            "chain_name": chain.name,
            "contract_name": result.get("ContractName", ""),
            "compiler": result.get("CompilerVersion", ""),
            "source_code": source_code,
            "source_type": "etherscan",
        }

    except Exception as e:
        logger.debug(f"  ⚠️ Etherscan API failed for {chain.name}: {e}")
        return None


def _try_blockscout_api(address: str, chain: EVMChain) -> Optional[dict]:
    """Try Blockscout explorer API."""
    # Build Blockscout API URL
    # Blockscout: {explorer_url}/api?module=contract&action=getsourcecode&address=0x...
    blockscout_api = chain.explorer_api.rstrip("/")
    
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
    }

    url = f"{blockscout_api}?{urlencode(params)}"

    try:
        req = Request(url, headers={"User-Agent": "MaatEye/1.0"})
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        if data.get("status") != "1":
            return None

        result = data.get("result", [{}])[0]
        source_code = result.get("SourceCode", "")
        if not source_code:
            return None

        # Same normalization as the Etherscan path (Blockscout can also return
        # Standard-JSON for multi-file verified contracts).
        flat, _ = flatten_sources(source_code)
        if flat:
            source_code = flat

        return {
            "address": address,
            "chain": chain.key,
            "chain_name": chain.name,
            "contract_name": result.get("ContractName", ""),
            "compiler": result.get("CompilerVersion", ""),
            "source_code": source_code,
            "source_type": "blockscout",
        }

    except Exception as e:
        logger.debug(f"  ⚠️ Blockscout API failed for {chain.name}: {e}")
        return None


def _try_rpc_bytecode(address: str, chain: EVMChain) -> Optional[dict]:
    """Last resort: check if address is a contract via RPC (no source)."""
    try:
        from urllib.request import urlopen, Request as R

        payload = json.dumps({
            "jsonrpc": "2.0", "id": 1,
            "method": "eth_getCode",
            "params": [address, "latest"],
        }).encode()

        req = R(chain.rpc_url, data=payload, headers={
            "Content-Type": "application/json",
            "User-Agent": "MaatEye/1.0",
        })
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        code = data.get("result", "0x")
        if code and code != "0x" and code != "0x0":
            return {
                "address": address,
                "chain": chain.key,
                "chain_name": chain.name,
                "contract_name": f"Unknown ({address[:8]}...)",
                "compiler": "unknown (bytecode only)",
                "source_code": f"// ⚠️ Contract on {chain.name} — source not verified\n"
                              f"// Address: {address}\n"
                              f"// Bytecode length: {len(code)} hex chars\n"
                              f"// Cannot scan without verified source code.\n",
                "source_type": "bytecode_only",
            }
    except Exception:
        pass

    return None


def format_chain_summary(chain: EVMChain) -> str:
    """Format a chain for display."""
    return (
        f"{chain.emoji} {chain.name} "
        f"(chainId: {chain.chain_id}, {chain.symbol})"
    )
