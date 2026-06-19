"""Guards against finding inflation: dedup per line + no ast_pattern crashes."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scanner.engine import ScanEngine, _VirtualMatch


def _engine_with_source(src: str) -> ScanEngine:
    eng = ScanEngine(chain_key="ethereum")
    eng._fetch_source = lambda a: {
        "source_code": src,
        "contract_name": "T",
        "compiler": "0.8.20",
        "chain": "ethereum",
        "chain_name": "Ethereum",
        "source_type": "test",
    }
    return eng


def test_virtualmatch_has_full_api():
    m = _VirtualMatch()
    # The recording loop calls all four — none may raise.
    assert m.start() == 0
    assert m.end() == 0
    assert m.group() == ""
    assert m.groups() == ()


def test_no_pattern_crashes_on_real_ish_contract():
    # Includes proxy/delegatecall/timestamp constructs that exercise the
    # previously-crashing ast_pattern detectors (P26/P27/P39/P44).
    src = (
        "pragma solidity 0.8.20;\n"
        "contract Proxy {\n"
        "  address impl;\n"
        "  function upgrade(address a) public { impl = a; }\n"
        "  fallback() external payable {\n"
        "    (bool ok,) = impl.delegatecall(msg.data);\n"
        "    require(ok);\n"
        "  }\n"
        "  function t() public view returns (uint) { return block.timestamp; }\n"
        "}\n"
    )
    eng = _engine_with_source(src)
    res = eng._scan_single("0xtest")
    # Must complete and produce a finite, small number of findings — no crash.
    assert not res.error
    assert res.vuln_count >= 0


def test_findings_deduped_per_line():
    # Same vuln keyword repeated on distinct lines => one finding per line;
    # repeated on the SAME line => still one finding.
    src = (
        "contract C {\n"
        "  function a() public view returns (uint) { return block.timestamp; }\n"  # line 2
        "  function b() public view returns (uint) { return block.timestamp; }\n"  # line 3
        "  function c() public view returns (uint) { return block.timestamp + block.timestamp; }\n"  # line 4, twice
        "}\n"
    )
    eng = _engine_with_source(src)
    res = eng._scan_single("0xtest")
    p20 = [v for v in res.vulnerabilities if v.pattern_id == "P20"]
    lines = {v.evidence for v in p20}
    # 3 distinct lines, not 4 (the double-occurrence on line 4 collapses).
    assert len(p20) == 3, f"expected 3 deduped P20 findings, got {len(p20)}: {lines}"
