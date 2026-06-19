"""
Source preparation for accurate static analysis.

Verified-source explorers (Etherscan/Blockscout) return one of:
  1. A single flat .sol file.
  2. A Solidity "Standard JSON Input" object: {"language":..., "sources":{path:{content}}}.
  3. The same Standard JSON wrapped in an extra pair of braces — Etherscan's
     multi-file quirk: ``{{"language":...}}``. Naive ``json.loads`` fails on the
     double brace, so callers used to scan the raw escaped-JSON blob (every
     bundled dependency file + comments + literal ``\\n``), which produced
     dozens of false-positive pattern hits per contract.

This module normalizes all three shapes into clean Solidity that contains only
the *project's own* code (third-party libraries filtered out) with comments and
string literals removed, so regex/heuristic patterns match real logic instead
of dependency boilerplate or prose.
"""

from __future__ import annotations

import json
import re
from typing import List, Tuple

# Path fragments that mark a file as a third-party dependency rather than the
# audited project's own source. Matched case-insensitively against the file path
# reported in the Standard-JSON ``sources`` map.
DEPENDENCY_MARKERS: Tuple[str, ...] = (
    "node_modules/",
    "@openzeppelin",
    "openzeppelin-",
    "openzeppelin/contracts",
    "@uniswap",
    "@chainlink",
    "@aave",
    "/lib/",
    "lib/forge-std",
    "forge-std/",
    "solmate/",
    "solady/",
    "@solmate",
    "@solady",
    "ds-test/",
    "hardhat/",
    "@ensdomains",
)


def _is_dependency(path: str) -> bool:
    p = path.lower()
    return any(marker in p for marker in DEPENDENCY_MARKERS)


def _maybe_unwrap_double_brace(raw: str) -> str:
    """Etherscan wraps Standard-JSON as ``{{ ... }}``; strip one outer pair."""
    s = raw.strip()
    if s.startswith("{{") and s.endswith("}}"):
        return s[1:-1]
    return s


def flatten_sources(raw: str, include_dependencies: bool = False) -> Tuple[str, List[str]]:
    """Flatten verified source into clean Solidity.

    Returns ``(combined_source, file_paths)``. ``file_paths`` is the list of
    source files actually kept (useful for diagnostics/tests). For a plain
    single-file contract the path list is ``["<flat>"]``.

    Dependency files are dropped unless ``include_dependencies`` is True. If
    *every* file looks like a dependency (e.g. the project re-exports a library
    directly), we fall back to keeping all of them rather than returning nothing.
    """
    if not raw:
        return "", []

    candidate = _maybe_unwrap_double_brace(raw)

    # Not JSON → already a flat .sol file.
    if not candidate.lstrip().startswith("{"):
        return raw, ["<flat>"]

    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        # Unparseable — return as-is so we never lose data, but the caller's
        # comment stripping still helps.
        return raw, ["<unparsed-json>"]

    # Standard JSON Input puts files under "sources"; some explorers return the
    # sources map directly (path -> {content}).
    sources = parsed.get("sources") if isinstance(parsed, dict) else None
    if sources is None and isinstance(parsed, dict):
        # Heuristic: a bare {path: {"content": ...}} map.
        if parsed and all(isinstance(v, dict) and "content" in v for v in parsed.values()):
            sources = parsed
    if not sources:
        # JSON but not a recognizable sources container — treat as flat.
        return raw, ["<flat>"]

    kept: List[Tuple[str, str]] = []
    for path, entry in sources.items():
        content = entry.get("content", "") if isinstance(entry, dict) else ""
        if not content:
            continue
        if not include_dependencies and _is_dependency(path):
            continue
        kept.append((path, content))

    # All files were dependencies → keep everything rather than nothing.
    if not kept:
        for path, entry in sources.items():
            content = entry.get("content", "") if isinstance(entry, dict) else ""
            if content:
                kept.append((path, content))

    combined = "\n\n".join(f"// File: {path}\n{content}" for path, content in kept)
    return combined, [path for path, _ in kept]


# Matches // line comments and /* block */ comments, and string/char literals,
# so we can blank them out before pattern matching (avoids matching vuln
# keywords that appear in prose or in revert-message strings).
_COMMENT_OR_STRING = re.compile(
    r"""
      //[^\n]*                |   # line comment
      /\*.*?\*/               |   # block comment
      "(?:\\.|[^"\\])*"       |   # double-quoted string
      '(?:\\.|[^'\\])*'           # single-quoted string
    """,
    re.DOTALL | re.VERBOSE,
)


def strip_comments(src: str) -> str:
    """Replace comments and string literals with equivalent whitespace.

    Newlines are preserved so line numbers (and therefore finding locations)
    stay accurate after stripping.
    """
    def _blank(m: re.Match) -> str:
        return re.sub(r"[^\n]", " ", m.group(0))

    return _COMMENT_OR_STRING.sub(_blank, src)


def prepare_for_scan(raw: str, include_dependencies: bool = False) -> str:
    """Full pipeline: flatten Standard-JSON → drop deps → strip comments/strings.

    The ``// File: <path>`` markers added during flattening are kept (they help
    locate findings) and are themselves stripped of trailing comment text by the
    comment pass only on their own line, which is harmless.
    """
    combined, _ = flatten_sources(raw, include_dependencies=include_dependencies)
    return strip_comments(combined)
