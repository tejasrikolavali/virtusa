from pathlib import Path

from src.fraud_copilot.mcp.client import run_mcp_tools

def test_ac10_mcp_integration():
    text = Path("src/fraud_copilot/mcp/client.py").read_text(encoding="utf-8")
    assert "langchain_mcp_adapters" in text
    assert "MultiServerMCPClient" in text

    transcript = run_mcp_tools("ORDER-001")
    assert any(item.get("tool") == "order_lookup" and item.get("status") == "success" for item in transcript)
    assert any(item.get("resource") == "fraud://policy-catalog" and item.get("status") == "success" for item in transcript)
