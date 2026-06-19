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


ERC20_TRANSFER = """pragma solidity 0.8.20;
contract T {
    mapping(address => uint256) bal;
    function transfer(address to, uint256 amount) external returns (bool) {
        bal[msg.sender] -= amount; bal[to] += amount; return true;
    }
    function payOut(address other, uint256 amt) external {
        IERC20(other).transfer(msg.sender, amt);  // ERC20 transfer — NOT a gas-stipend issue
    }
}
interface IERC20 { function transfer(address, uint256) external returns (bool); }"""

ETH_TRANSFER = """pragma solidity 0.8.20;
contract W {
    function withdraw(uint256 amt) external { payable(msg.sender).transfer(amt); }
}"""


def test_erc20_transfer_not_flagged_as_gas_stipend():
    # ERC20 `.transfer(to, amount)` (two args) must NOT trigger P42.
    assert "P42" not in _pattern_ids(_scan(ERC20_TRANSFER))


def test_eth_transfer_is_flagged_as_gas_stipend():
    # ETH `.transfer(amount)` (single arg) SHOULD trigger P42.
    assert "P42" in _pattern_ids(_scan(ETH_TRANSFER))


VIEW_AND_CALL_BUT_SEPARATE = """pragma solidity 0.8.20;
contract S {
    function balance() external view returns (uint256) { return address(this).balance; }
    function exec(address t, bytes calldata d) external { (bool ok,) = t.call(d); require(ok); }
}"""

VIEW_MAKES_CALL = """pragma solidity 0.8.20;
contract O {
    function price(address oracle) external view returns (uint256) {
        (bool ok, bytes memory r) = oracle.staticcall(abi.encodeWithSignature("get()"));
        require(ok); return abi.decode(r, (uint256));
    }
}"""


def test_view_and_call_in_separate_functions_not_flagged_p26():
    # A view function and a low-level call in DIFFERENT functions must not trip
    # P26 (the removed ast_pattern fired on mere co-occurrence).
    assert "P26" not in _pattern_ids(_scan(VIEW_AND_CALL_BUT_SEPARATE))


def test_view_making_external_call_is_flagged_p26():
    assert "P26" in _pattern_ids(_scan(VIEW_MAKES_CALL))


def test_eth_transfer_not_flagged_as_no_safe_erc20():
    # P19 is about raw ERC20 transfers; ETH single-arg transfer must not trip it.
    assert "P19" not in _pattern_ids(_scan(ETH_TRANSFER))


def test_raw_erc20_transfer_flagged_p19():
    raw = ("pragma solidity 0.8.20; contract C { function f(address t) external {"
           " IERC20(t).transfer(msg.sender, 1); } }"
           " interface IERC20 { function transfer(address,uint256) external returns (bool); }")
    assert "P19" in _pattern_ids(_scan(raw))


def test_unprotected_mint_is_caught():
    assert "P01" in _pattern_ids(_scan(VULN_UNPROTECTED_MINT))


def test_tx_origin_auth_is_caught():
    assert "P05" in _pattern_ids(_scan(VULN_TX_ORIGIN_AUTH))
