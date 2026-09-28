from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REQUIRED=[
"src/graph.py","src/context/pipeline.py","src/memory/manager.py",
"tests/test_memory_persistence.py","src/tools/rag_tool.py","mcp_server/server.py",
"src/observability/tracing.py","logs/tool_calls.jsonl","logs/memory_test.log","docs/failure-analysis.md",
"reports/golden_signals.json","reports/dashboard.png","reports/dashboard_data.csv",
"src/guardrails/io.py","logs/agent_actions.jsonl",".env.example",".gitignore",
"docs/risk-register.md","docs/model-card.md","docs/compliance.md","docs/output-risk.md",
"reports/eval_report.json","tests/test_routing.py","tests/test_loops.py",
"tests/test_tool_contracts.py","README.md"]
missing=[p for p in REQUIRED if not (ROOT/p).exists()]
print("MISSING:")
for p in missing: print(" -",p)
if not missing: print("All required paths exist; inspect TODOs/evidence before submission.")
