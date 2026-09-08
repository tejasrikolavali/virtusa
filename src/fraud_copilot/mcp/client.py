import asyncio
import sys
from pathlib import Path

async def get_mcp_tools():
    """Consume the custom MCP server through langchain-mcp-adapters."""
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain_mcp_adapters.tools import load_mcp_tools
    server = Path(__file__).resolve().parents[3] / "mcp_server" / "server.py"
    client = MultiServerMCPClient({
        "fraud_tools": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [str(server)],
        }
    })
    async with client.session("fraud_tools") as session:
        return await load_mcp_tools(session)

async def invoke_mcp_tools(order_id: str):
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain_mcp_adapters.tools import load_mcp_tools
    server = Path(__file__).resolve().parents[3] / "mcp_server" / "server.py"
    client = MultiServerMCPClient({
        "fraud_tools": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [str(server)],
        }
    })
    async with client.session("fraud_tools") as session:
        tools = await load_mcp_tools(session)
        by_name = {getattr(tool, "name", ""): tool for tool in tools}
        transcript = []
        for name in ("order_lookup", "payment_check"):
            tool = by_name.get(name)
            if tool is None:
                transcript.append({"tool": name, "status": "not_discovered"})
                continue
            arguments = {"order_id": order_id}
            try:
                result = await asyncio.wait_for(tool.ainvoke(arguments), timeout=10)
                transcript.append({
                    "tool": name,
                    "arguments": arguments,
                    "result": result,
                    "status": "success",
                })
            except Exception as exc:
                transcript.append({
                    "tool": name,
                    "arguments": arguments,
                    "status": "error",
                    "error": str(exc),
                })
        try:
            resource = await asyncio.wait_for(
                session.read_resource("fraud://policy-catalog"), timeout=10
            )
            resource_result = resource.model_dump(mode="json")
            transcript.append({
                "resource": "fraud://policy-catalog",
                "result": resource_result,
                "status": "success",
            })
        except Exception as exc:
            transcript.append({
                "resource": "fraud://policy-catalog",
                "status": "error",
                "error": str(exc),
            })
        return transcript

def demo_mcp_call():
    """Exercise adapter integration and return a transcript-friendly result."""
    async def _run():
        tools = await get_mcp_tools()
        names = [getattr(t, "name", str(t)) for t in tools]
        return {"tools_discovered": names, "adapter": "langchain-mcp-adapters"}
    return asyncio.run(_run())

def run_mcp_tools(order_id: str):
    """Invoke domain MCP tools with an explicit, serializable transcript."""
    try:
        return asyncio.run(invoke_mcp_tools(order_id))
    except Exception as exc:
        return [{"status": "error", "error": str(exc)}]
