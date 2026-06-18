"""MaatEye — Etherscan API Fetcher
Fetches verified contract source code from Etherscan.
"""

import json
import time
from typing import Optional
from urllib.request import urlopen, Request
from urllib.parse import urlencode

from scanner.utils.config import load_config
from scanner.utils.logger import get_logger

logger = get_logger(__name__)

# Simple in-memory cache
_source_cache: dict[str, dict] = {}
_last_request_time: float = 0


def fetch_contract_source(address: str, network: str = "mainnet") -> Optional[dict]:
    """Fetch a verified contract's source code from Etherscan."""
    global _last_request_time

    # Check cache first
    cache_key = f"{network}:{address.lower()}"
    if cache_key in _source_cache:
        logger.debug(f"  📦 Cache hit for {address}")
        return _source_cache[cache_key]

    config = load_config()
    api_key = config.get("etherscan", {}).get("api_key", "YourApiKeyToken")
    rate_limit = config.get("etherscan", {}).get("rate_limit", 5)

    # Rate limiting
    elapsed = time.time() - _last_request_time
    if elapsed < 1.0 / rate_limit:
        time.sleep(1.0 / rate_limit - elapsed)

    network_config = config.get("networks", {}).get(network, {})
    base_url = network_config.get("etherscan_api",
                                   f"https://api.etherscan.io/api")

    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": api_key,
    }

    url = f"{base_url}?{urlencode(params)}"

    try:
        req = Request(url, headers={"User-Agent": "MaatEye/1.0"})
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        _last_request_time = time.time()

        if data.get("status") != "1":
            logger.debug(f"  ⚠️ Etherscan: {data.get('message', 'Unknown error')}")
            return None

        result = data.get("result", [{}])[0]
        source_code = result.get("SourceCode", "")

        if not source_code:
            logger.debug(f"  ⚠️ No source code for {address}")
            return None

        # Handle Solidity standard JSON input
        if source_code.startswith("{"):
            try:
                parsed = json.loads(source_code)
                # Extract the main contract source
                sources = parsed.get("sources", {})
                combined = []
                for path, content in sources.items():
                    combined.append(f"// File: {path}\n{content.get('content', '')}")
                source_code = "\n\n".join(combined)
            except json.JSONDecodeError:
                pass

        result_dict = {
            "address": address,
            "contract_name": result.get("ContractName", ""),
            "compiler": result.get("CompilerVersion", ""),
            "source_code": source_code,
            "abi": result.get("ABI", ""),
            "constructor_args": result.get("ConstructorArguments", ""),
            "swarm_source": result.get("SwarmSource", ""),
            "library": result.get("Library", ""),
            "license_type": result.get("LicenseType", ""),
            "proxy": result.get("Proxy", "0"),
            "implementation": result.get("Implementation", ""),
            "optimization_used": result.get("OptimizationUsed", ""),
            "runs": result.get("Runs", ""),
        }

        # Cache it
        _source_cache[cache_key] = result_dict

        logger.debug(f"  ✅ Fetched source for {address}"
                      f" ({result_dict['contract_name']}, "
                      f"{len(source_code)} bytes)")
        return result_dict

    except Exception as e:
        logger.warning(f"  ⚠️ Failed to fetch {address}: {e}")
        return None
