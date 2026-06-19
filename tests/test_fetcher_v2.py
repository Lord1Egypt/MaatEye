"""Etherscan V2 unified-API selection (the fix that unlocks non-Avalanche chains)."""

import sys
import io
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import scanner.fetchers.multichain as mc
from scanner.chains import EVM_CHAINS


def _capture_url(monkey_src: str = "contract C {}"):
    """Patch urlopen to record the URL and return a minimal verified response."""
    captured = {}

    class _Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_urlopen(req, timeout=0):
        captured["url"] = req.full_url if hasattr(req, "full_url") else str(req)
        body = json.dumps({
            "status": "1",
            "result": [{"SourceCode": monkey_src, "ContractName": "C", "CompilerVersion": "0.8.20"}],
        }).encode()
        return _Resp(body)

    return captured, fake_urlopen


def test_uses_v2_unified_endpoint_with_key(monkeypatch):
    captured, fake = _capture_url()
    monkeypatch.setattr(mc, "urlopen", fake)
    res = mc._try_etherscan_api("0xabc", EVM_CHAINS["base"], api_key="KEY123")
    assert res and res["source_type"] == "etherscan"
    assert "api.etherscan.io/v2" in captured["url"]
    assert "chainid=8453" in captured["url"]   # Base
    assert "apikey=KEY123" in captured["url"]


def test_falls_back_to_native_endpoint_without_key(monkeypatch):
    captured, fake = _capture_url()
    monkeypatch.setattr(mc, "urlopen", fake)
    res = mc._try_etherscan_api("0xabc", EVM_CHAINS["avalanche"], api_key="")
    assert res and res["source_type"] == "etherscan"
    # Keyless path uses the chain's own (Snowtrace) endpoint, not V2.
    assert "snowtrace.io" in captured["url"]
    assert "v2" not in captured["url"]
