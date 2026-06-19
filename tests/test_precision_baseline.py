"""Precision baseline — the foundation for incremental pattern tuning.

This is a labeled fixture set: contracts with a *known* status. It guards two
directions at once so future pattern changes are honest:

  - FALSE POSITIVES: a clean, standard contract must stay (near-)silent.
  - TRUE POSITIVES:  a contract with a known issue must be flagged for the
                     right pattern.

When tightening a noisy pattern, run this: clean fixtures must not regress into
noise, and the known-vuln fixtures must still be caught. Add a fixture here for
every pattern you tune.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scanner.engine import ScanEngine


def _scan(src: str):
    eng = ScanEngine(chain_key="ethereum")
    eng._fetch_source = lambda a: {
        "source_code": src, "contract_name": "T", "compiler": "0.8.20",
        "chain": "ethereum", "chain_name": "Ethereum", "source_type": "test",
    }
    return eng._scan_single("0x0")


def _pattern_ids(res):
    return {v.pattern_id for v in res.vulnerabilities}


# ── Clean fixtures: must stay quiet (false-positive guard) ──────────────────

CLEAN_ERC20 = """// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;
contract Token {
    mapping(address => uint256) public balanceOf;
    uint256 public totalSupply;
    address public owner;
    constructor(uint256 supply) { owner = msg.sender; totalSupply = supply; balanceOf[msg.sender] = supply; }
    function transfer(address to, uint256 amt) external returns (bool) {
        require(to != address(0), "zero");
        require(balanceOf[msg.sender] >= amt, "bal");
        balanceOf[msg.sender] -= amt;
        balanceOf[to] += amt;
        return true;
    }
}"""


def test_clean_erc20_has_no_critical_false_positives():
    res = _scan(CLEAN_ERC20)
    assert res.critical_count == 0, f"clean ERC20 raised critical flags: {_pattern_ids(res)}"
    # Budget: a plain, safe token should be essentially silent. If a pattern
    # change pushes this up, it is adding false positives — investigate.
    assert res.vuln_count <= 1, f"clean ERC20 flag budget exceeded: {res.vuln_count} {_pattern_ids(res)}"


# ── Vulnerable fixtures: must be caught (true-positive guard) ────────────────

VULN_UNPROTECTED_MINT = """// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;
contract Bad {
    mapping(address => uint256) public balanceOf;
    uint256 public totalSupply;
    function mint(address to, uint256 amt) external { balanceOf[to] += amt; totalSupply += amt; }
}"""

VULN_TX_ORIGIN_AUTH = """pragma solidity 0.8.20;
contract Auth {
    address owner;
    function withdraw() external {
        require(tx.origin == owner, "no");
        payable(msg.sender).transfer(address(this).balance);
    }
}"""


def test_unprotected_mint_is_caught():
    assert "P01" in _pattern_ids(_scan(VULN_UNPROTECTED_MINT))


def test_tx_origin_auth_is_caught():
    assert "P05" in _pattern_ids(_scan(VULN_TX_ORIGIN_AUTH))
