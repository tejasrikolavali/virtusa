from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def exists(p):
    return (ROOT / p).exists()

def main():
    checks = {}
    for i in range(1,13):
        matches = list((ROOT/"tests").glob(f"test_ac{i:02d}_*.py"))
        checks[f"AC-{i:02d} test"] = bool(matches)

    required = {
        "README": "README.md",
        ".env.example": ".env.example",
        "business case": "docs/business-case.md",
        "architecture": "docs/architecture.md",
        "context engineering": "docs/context-engineering.md",
        "memory policy": "docs/memory-policy.md",
        "MCP decision": "docs/mcp-decision.md",
        "MCP server": "mcp_server/server.py",
        "typed state": "src/fraud_copilot/state.py",
        "graph builder": "src/fraud_copilot/graph/builder.py",
        "sample data": "data/orders/sample_orders.json",
    }
    print("="*68)
    print("FINAL PROJECT AUDIT")
    print("="*68)
    for name, path in required.items():
        print(f"{name:28} {'PASS' if exists(path) else 'FAIL'}")
    for name, value in checks.items():
        if name.endswith(" test"):
            print(f"{name:28} {'PASS' if value else 'FAIL'}")
    print("\nRun: python -m pytest -q")
    print("Then run: python scripts/run_memory_test.py")
    print("Then run: python scripts/run_mcp_demo.py")
    print("Then run: python scripts/run_rag_demo.py")
    print("="*68)

if __name__ == "__main__":
    main()
