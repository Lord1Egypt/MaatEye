"""MaatEye — Test patterns against sample Solidity code."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scanner.engine import ScanEngine
from scanner.utils.config import load_config, get_all_patterns


# Sample vulnerable contracts
UNPROTECTED_MINT = """
pragma solidity 0.8.0;

contract BadToken {
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;

    function mint(address to, uint256 amount) public {
        totalSupply += amount;
        balanceOf[to] += amount;
    }
}
"""

SAFE_MINT = """
pragma solidity 0.8.0;

contract GoodToken {
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;
    address public owner;

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    function mint(address to, uint256 amount) public onlyOwner {
        totalSupply += amount;
        balanceOf[to] += amount;
    }
}
"""

SELFDESTRUCT_ANYONE = """
pragma solidity 0.8.0;

contract Killable {
    function kill() public {
        selfdestruct(payable(msg.sender));
    }
}
"""

TX_ORIGIN_AUTH = """
pragma solidity 0.8.0;

contract Phishable {
    address public owner;

    function transfer(address to, uint256 amount) public {
        require(tx.origin == owner);
        // send amount
    }
}
"""

REENTRANCY = """
pragma solidity 0.8.0;

contract VulnerableBank {
    mapping(address => uint256) public balances;

    function withdraw() public {
        uint256 amount = balances[msg.sender];
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success);
        balances[msg.sender] = 0;
    }
}
"""

OVERFLOW = """
pragma solidity 0.7.0;

contract OverflowToken {
    uint256 public totalSupply;

    function addSupply(uint256 amount) public {
        totalSupply += amount;
    }
}
"""


def test_unprotected_mint():
    """P01 should detect unprotected mint."""
    engine = ScanEngine()
    config = load_config()
    patterns = get_all_patterns(config)
    p01 = patterns.get("P01")
    assert p01 is not None, "P01 pattern not found"

    # We can't easily test without a real fetch, but we test the pattern exists
    assert p01["id"] == "P01"
    assert p01["severity"] == "critical"
    assert len(p01["detectors"]) > 0


def test_patterns_loaded():
    """All 20 plagues should be loaded."""
    engine = ScanEngine()
    assert len(engine.active_patterns) >= 20, \
        f"Expected 20+ patterns, got {len(engine.active_patterns)}"


def test_selfdestruct_pattern():
    """P02 pattern should exist."""
    config = load_config()
    patterns = get_all_patterns(config)
    assert "P02" in patterns
    assert patterns["P02"]["name"] == "Selfdestruct Anyone"


def test_tx_origin_pattern():
    """P05 pattern should exist."""
    config = load_config()
    patterns = get_all_patterns(config)
    assert "P05" in patterns
    assert patterns["P05"]["severity"] == "high"


def test_all_patterns_have_required_fields():
    """Every pattern must have id, name, severity, detectors."""
    config = load_config()
    patterns = get_all_patterns(config)
    for pid, p in patterns.items():
        assert "id" in p, f"{pid} missing id"
        assert "name" in p, f"{pid} missing name"
        assert "severity" in p, f"{pid} missing severity"
        assert "detectors" in p, f"{pid} missing detectors"
        assert len(p["detectors"]) > 0, f"{pid} has no detectors"
