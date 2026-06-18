import os
import gzip
import random
from scanner.utils.logger import get_logger

logger = get_logger(__name__)

# Global cache so we only decompress once per workflow run
_eth_cache = []

def get_ethereum_tokens_from_local_db(max_count: int = 500, exclude_set: set = None) -> list[str]:
    """Fetch random unscanned Ethereum tokens from the massive local gzip DB."""
    global _eth_cache
    
    db_path = "data/eth_addresses.txt.gz"
    
    if not os.path.exists(db_path):
        return []

    exclude_set = exclude_set or set()

    if not _eth_cache:
        logger.info("  📂 Decompressing local Ethereum token database (1.45M tokens)...")
        try:
            with gzip.open(db_path, "rt", encoding="utf-8") as f:
                for line in f:
                    addr = line.strip().lower()
                    if len(addr) == 42 and addr.startswith("0x"):
                        _eth_cache.append(addr)
            logger.info(f"  📂 Successfully loaded {len(_eth_cache)} tokens.")
        except Exception as e:
            logger.warning(f"  ⚠️ Failed to read local database: {e}")
            return []

    # Find tokens that aren't in exclude_set
    # We do a quick filter to find unscanned tokens
    unscanned = [addr for addr in _eth_cache if addr not in exclude_set]
    
    if not unscanned:
        return []
        
    # Pick a random sample
    sample_size = min(max_count, len(unscanned))
    selected = random.sample(unscanned, sample_size)
    
    logger.debug(f"  📂 Selected {len(selected)} random unscanned tokens from local DB")
    return selected
