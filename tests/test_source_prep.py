"""Tests for source normalization and finding accuracy (false-positive guards)."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scanner.utils.source_prep import (
    flatten_sources,
    strip_comments,
    prepare_for_scan,
    _is_dependency,
)


def test_plain_solidity_passthrough():
    src = "pragma solidity ^0.8.0;\ncontract A { function f() public {} }"
    combined, paths = flatten_sources(src)
    assert "contract A" in combined
    assert paths == ["<flat>"]


def test_standard_json_flattened():
    raw = json.dumps({
        "language": "Solidity",
        "sources": {
            "src/Token.sol": {"content": "contract Token { uint x; }"},
            "src/Vault.sol": {"content": "contract Vault { uint y; }"},
        },
    })
    combined, paths = flatten_sources(raw)
    assert "contract Token" in combined and "contract Vault" in combined
    assert set(paths) == {"src/Token.sol", "src/Vault.sol"}


def test_etherscan_double_brace_unwrapped():
    """Etherscan wraps Standard-JSON as {{...}} — must still parse."""
    inner = {
        "language": "Solidity",
        "sources": {"src/Main.sol": {"content": "contract Main { }"}},
    }
    raw = "{" + json.dumps(inner) + "}"  # double-wrapped
    combined, paths = flatten_sources(raw)
    assert "contract Main" in combined
    assert paths == ["src/Main.sol"]


def test_dependencies_dropped():
    raw = json.dumps({
        "sources": {
            "src/MyToken.sol": {"content": "contract MyToken {}"},
            "@openzeppelin/contracts/token/ERC20/ERC20.sol": {"content": "contract ERC20 { uint a; }"},
            "node_modules/@uniswap/v3/Pool.sol": {"content": "contract Pool {}"},
        },
    })
    combined, paths = flatten_sources(raw)
    assert "contract MyToken" in combined
    assert "contract ERC20" not in combined
    assert "contract Pool" not in combined
    assert paths == ["src/MyToken.sol"]


def test_all_dependencies_keeps_everything():
    """If every file looks like a dep, don't return empty — keep them."""
    raw = json.dumps({
        "sources": {"@openzeppelin/contracts/proxy/Proxy.sol": {"content": "contract Proxy {}"}},
    })
    combined, paths = flatten_sources(raw)
    assert "contract Proxy" in combined


def test_is_dependency_markers():
    assert _is_dependency("@openzeppelin/contracts/access/Ownable.sol")
    assert _is_dependency("node_modules/foo/Bar.sol")
    assert _is_dependency("lib/forge-std/src/Test.sol")
    assert not _is_dependency("src/MyVault.sol")
    assert not _is_dependency("contracts/Token.sol")


def test_strip_comments_preserves_line_numbers():
    src = "line1 // a comment\n/* block\ncomment */ contract C {}\nstring s = \"selfdestruct\";"
    out = strip_comments(src)
    # vuln keyword inside a string literal must not survive
    assert "selfdestruct" not in out
    # comment text gone
    assert "comment" not in out
    # line count preserved so finding locations stay correct
    assert out.count("\n") == src.count("\n")
    # real code kept
    assert "contract C {}" in out


def test_prepare_for_scan_end_to_end():
    raw = json.dumps({
        "sources": {
            "src/Main.sol": {"content": "// kill switch\ncontract Main { function f() public { selfdestruct(payable(msg.sender)); } }"},
            "@openzeppelin/contracts/utils/Address.sol": {"content": "library Address { function sendValue() internal { selfdestruct(payable(tx.origin)); } }"},
        },
    })
    out = prepare_for_scan(raw)
    # project selfdestruct kept (real code), dependency one dropped
    assert out.count("selfdestruct") == 1
    # comment removed
    assert "kill switch" not in out
