"""MaatEye — Local Cache for Contract Source Code."""

import json
from pathlib import Path
from typing import Optional

from scanner.utils.logger import get_logger

logger = get_logger(__name__)

CACHE_DIR = Path(__file__).parent.parent.parent / "results" / "cache"


def get_contract_from_cache(address: str) -> Optional[dict]:
    """Load contract source from local cache if available and fresh."""
    cache_file = CACHE_DIR / f"{address.lower()}.json"

    if not cache_file.exists():
        return None

    try:
        with open(cache_file) as f:
            data = json.load(f)
        logger.debug(f"  📦 Cache hit: {address}")
        return data
    except (json.JSONDecodeError, IOError):
        return None


def save_contract_to_cache(address: str, data: dict) -> None:
    """Save contract source to local cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{address.lower()}.json"

    try:
        with open(cache_file, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        logger.warning(f"  ⚠️ Failed to cache {address}: {e}")


def clear_cache() -> int:
    """Clear all cached contract sources. Returns count of cleared files."""
    if not CACHE_DIR.exists():
        return 0

    count = 0
    for f in CACHE_DIR.glob("*.json"):
        f.unlink()
        count += 1

    logger.info(f"🗑️ Cleared {count} cached contracts")
    return count
