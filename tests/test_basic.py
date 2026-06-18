"""MaatEye — Basic tests for the scanner engine."""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scanner.engine import ScanEngine, Vulnerability, ContractResult, ScanResults


def test_vulnerability_creation():
    """Test basic Vulnerability creation."""
    v = Vulnerability(
        pattern_id="P01",
        pattern_name="Unprotected Mint",
        severity="critical",
        contract="0x1234",
        contract_name="TestToken",
        description="Test",
        location="line 42",
        snippet="function mint()",
        evidence="Match at 100",
        confidence=0.85,
        recommendation="Add onlyOwner",
    )
    assert v.pattern_id == "P01"
    assert v.severity == "critical"
    assert v.confidence == 0.85


def test_contract_result():
    """Test ContractResult aggregation."""
    c = ContractResult(
        address="0x1234",
        contract_name="Test",
        compiler="0.8.20",
        source_length=1000,
    )
    assert c.vuln_count == 0
    assert c.critical_count == 0

    c.vulnerabilities.append(
        Vulnerability(
            pattern_id="P01", pattern_name="Test", severity="critical",
            contract="0x1234", contract_name="Test", description="",
            location="", snippet="", evidence="", confidence=1.0,
            recommendation="",
        )
    )
    assert c.vuln_count == 1
    assert c.critical_count == 1


def test_scan_results():
    """Test ScanResults aggregation and serialization."""
    r = ScanResults(timestamp="2024-01-01T00:00:00Z")
    r.contracts["0x1234"] = ContractResult(
        address="0x1234",
        contract_name="Test",
        compiler="",
        source_length=0,
    )
    r.total_contracts = 1

    d = r.to_dict()
    assert d["total_contracts"] == 1
    assert "timestamp" in d


def test_vuln_count_per_severity():
    """Test severity-specific count methods."""
    c = ContractResult(address="0x1", contract_name="", compiler="", source_length=0)
    sevs = ["critical", "critical", "high", "medium", "low"]
    for s in sevs:
        c.vulnerabilities.append(
            Vulnerability(
                pattern_id="P99", pattern_name="Test", severity=s,
                contract="0x1", contract_name="", description="",
                location="", snippet="", evidence="", confidence=1.0,
                recommendation="",
            )
        )
    assert c.critical_count == 2
    assert c.high_count == 1
    assert c.medium_count == 1
