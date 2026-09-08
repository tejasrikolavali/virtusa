from pathlib import Path

def test_ac09_mcp():
    text = Path("mcp_server/server.py").read_text(encoding="utf-8")
    assert "@mcp.tool()" in text
    assert text.count("@mcp.tool()") >= 2
    assert "@mcp.resource" in text
