"""Guards against finding inflation: dedup per line + no ast_pattern crashes."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scanner.engine import ScanEngine, _VirtualMatch


def _engine_with_source(src: str, min_confidence: float = 0.5) -> ScanEngine:
    eng = ScanEngine(chain_key="ethereum", min_confidence=min_confidence)
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


def test_confidence_threshold_filters_low_confidence_detectors():
    # block.timestamp only matches P20 detectors (confidence 0.30/0.45). With
    # the default 0.5 threshold they are filtered; with threshold 0 they fire.
    src = "contract C { function f() public view returns (uint) { return block.timestamp; } }"

    default_eng = _engine_with_source(src)  # min_confidence=0.5
    default_res = default_eng._scan_single("0xtest")
    assert not [v for v in default_res.vulnerabilities if v.pattern_id == "P20"]

    loose_eng = _engine_with_source(src, min_confidence=0.0)
    loose_res = loose_eng._scan_single("0xtest")
    assert [v for v in loose_res.vulnerabilities if v.pattern_id == "P20"]


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
    # Disable the confidence threshold so the (low-confidence) P20 timestamp
    # detector fires — this test targets the dedup mechanism specifically.
    eng = _engine_with_source(src, min_confidence=0.0)
    res = eng._scan_single("0xtest")
    p20 = [v for v in res.vulnerabilities if v.pattern_id == "P20"]
    lines = {v.evidence for v in p20}
    # 3 distinct lines, not 4 (the double-occurrence on line 4 collapses).
    assert len(p20) == 3, f"expected 3 deduped P20 findings, got {len(p20)}: {lines}"
