import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.fraud_copilot.mcp.client import demo_mcp_call

def main():
    try:
        result = demo_mcp_call()
    except Exception as exc:
        result = {
            "adapter": "langchain-mcp-adapters",
            "status": "environment_check_failed",
            "error": str(exc),
        }
    out = Path("evidence/AC-10/mcp_tool_call_transcript.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"AC": "AC-10", **result}, indent=2), encoding="utf-8")
    print(out.read_text())

if __name__ == "__main__":
    main()
