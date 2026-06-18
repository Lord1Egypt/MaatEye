"""MaatEye — Utility functions."""

import hashlib
import json
import re
from pathlib import Path
from typing import Optional


def normalize_address(addr: str) -> str:
    """Normalize an Ethereum address to lowercase checksum format."""
    return addr.strip().lower()


def is_valid_ethereum_address(addr: str) -> bool:
    """Check if a string is a valid Ethereum address."""
    return bool(re.match(r'^0x[a-fA-F0-9]{40}$', addr.strip()))


def extract_addresses_from_text(text: str) -> list[str]:
    """Extract all Ethereum addresses from text."""
    return re.findall(r'0x[a-fA-F0-9]{40}', text)


def truncate_source(source: str, max_length: int = 500_000) -> str:
    """Truncate source code to a maximum length."""
    if len(source) <= max_length:
        return source
    return source[:max_length] + f"\n// ... truncated ({len(source) - max_length} bytes removed)"


def compute_contract_hash(source: str) -> str:
    """Compute a hash of the contract source for deduplication."""
    return hashlib.sha256(source.encode()).hexdigest()[:16]


def serialize_for_json(obj):
    """Serialize an object for JSON output."""
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    if isinstance(obj, (set, frozenset)):
        return list(obj)
    return str(obj)
