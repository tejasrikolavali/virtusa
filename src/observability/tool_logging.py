import json
import time
from datetime import datetime, timezone
from pathlib import Path


def log_tool_call(agent, tool_name, args, result, started, status="ok"):
    path = Path("logs/tool_calls.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "tool_name": tool_name,
        "args": args,
        "result": result,
        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        "status": status,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, default=str) + "\n")
    return row
