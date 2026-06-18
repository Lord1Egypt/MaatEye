"""
MaatEye — Configuration Manager
Loads patterns, settings, and manages the pattern index.
"""

import json
import os
import yaml
from pathlib import Path
from typing import Any, Optional

from scanner.utils.logger import get_logger

logger = get_logger(__name__)

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
PATTERNS_DIR = BASE_DIR / "scanner" / "patterns"
CONFIG_DIR = BASE_DIR / "config"
NEW_PATTERNS_DIR = PATTERNS_DIR / "new"
INDEX_FILE = CONFIG_DIR / "patterns_index.json"

DEFAULT_CONFIG = {
    "scanner": {
        "max_workers": 5,
        "timeout_seconds": 30,
        "max_source_size": 500_000,  # 500KB max source
        "cache_enabled": True,
        "cache_ttl_hours": 24,
    },
    "etherscan": {
        "api_key": os.environ.get("ETHERSCAN_API_KEY", ""),
        "base_url": "https://api.etherscan.io/api",
        "rate_limit": 5,  # requests per second
    },
    "networks": {
        "mainnet": {
            "name": "Ethereum Mainnet",
            "chain_id": 1,
            "etherscan_api": "https://api.etherscan.io/api",
        },
        "sepolia": {
            "name": "Sepolia Testnet",
            "chain_id": 11155111,
            "etherscan_api": "https://api-sepolia.etherscan.io/api",
        },
    },
    "reporting": {
        "max_vulns_per_contract": 50,
        "min_confidence_to_report": 0.3,
        "auto_create_issues": True,
        "red_flag_label": "🚩 Red Flag",
    },
}


def load_config() -> dict:
    """Load configuration, merging defaults with user config if exists."""
    config = DEFAULT_CONFIG.copy()
    config_file = CONFIG_DIR / "settings.json"

    if config_file.exists():
        try:
            with open(config_file) as f:
                user_config = json.load(f)
            _deep_merge(config, user_config)
            logger.debug(f"Loaded config from {config_file}")
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load config file: {e}")

    return config


def _deep_merge(base: dict, override: dict) -> None:
    """Deep merge two dictionaries."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def get_all_patterns(config: Optional[dict] = None, category: Optional[str] = None) -> dict:
    """Load all patterns from the patterns directory.
    
    Args:
        config: Optional config dict
        category: Optional category filter (e.g., "ACCESS_CONTROL", "REENTRANCY")
                 Only returns patterns matching this category.
    
    Returns:
        Dict of pattern_id -> pattern_data
    """
    if config is None:
        config = load_config()

    patterns = {}

    # Try loading from index first
    if INDEX_FILE.exists():
        try:
            with open(INDEX_FILE) as f:
                index = json.load(f)
                for entry in index:
                    pattern_file = PATTERNS_DIR / entry.get("file", "")
                    if pattern_file.exists():
                        pattern = _load_pattern_file(pattern_file)
                        if pattern:
                            pid = pattern.get("id", "")
                            patterns[pid] = pattern
            if patterns:
                logger.debug(f"Loaded {len(patterns)} patterns from index")
                # Don't return yet — apply filter below
        except (json.JSONDecodeError, IOError):
            logger.debug("Index load failed, scanning directory")

    # Only scan directory if index didn't give us patterns
    if not patterns:
        # Fallback: scan the patterns directory
        for yaml_file in sorted(PATTERNS_DIR.glob("P*.yaml")):
            pattern = _load_pattern_file(yaml_file)
            if pattern:
                pid = pattern.get("id", "")
                patterns[pid] = pattern

    # Also check new/ directory
    if NEW_PATTERNS_DIR.exists():
        for yaml_file in sorted(NEW_PATTERNS_DIR.glob("*.yaml")):
            pattern = _load_pattern_file(yaml_file)
            if pattern:
                pid = pattern.get("id", "")
                if pid not in patterns:
                    patterns[pid] = pattern

    # Apply category filter if specified
    if category is not None:
        filtered = {}
        for pid, pattern in patterns.items():
            if pattern.get("category", "").upper() == category.upper():
                filtered[pid] = pattern
        logger.debug(f"Filtered by category '{category}': {len(filtered)} patterns")
        return filtered

    logger.debug(f"Loaded {len(patterns)} patterns (scan fallback)")
    return patterns


def get_pattern_by_id(pattern_id: str) -> Optional[dict]:
    """Get a single pattern by its ID."""
    patterns = get_all_patterns()
    return patterns.get(pattern_id)


def _load_pattern_file(path: Path) -> Optional[dict]:
    """Load and validate a single pattern YAML file."""
    try:
        with open(path) as f:
            pattern = yaml.safe_load(f)
        if not pattern or "id" not in pattern or "name" not in pattern:
            logger.warning(f"Invalid pattern file: {path.name}")
            return None
        pattern["_file"] = path.name
        return pattern
    except yaml.YAMLError as e:
        logger.warning(f"YAML parse error in {path.name}: {e}")
        return None
    except IOError as e:
        logger.warning(f"IO error reading {path.name}: {e}")
        return None


def build_pattern_index() -> int:
    """Build the pattern index JSON file with full metadata."""
    patterns = []

    for yaml_file in sorted(PATTERNS_DIR.glob("P*.yaml")):
        pattern = _load_pattern_file(yaml_file)
        if pattern:
            patterns.append({
                "id": pattern.get("id", ""),
                "name": pattern.get("name", ""),
                "category": pattern.get("category", ""),
                "subcategory": pattern.get("subcategory", ""),
                "severity": pattern.get("severity", "medium"),
                "difficulty": pattern.get("difficulty", "medium"),
                "enabled": pattern.get("enabled", True),
                "requires_ast": pattern.get("requires_ast", False),
                "exploitability_estimate": pattern.get("exploitability_estimate", 0.5),
                "file": yaml_file.name,
            })

    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, "w") as f:
        json.dump(patterns, f, indent=2)

    logger.info(f"📝 Built pattern index: {len(patterns)} patterns")
    return len(patterns)
