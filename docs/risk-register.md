# Risk register

| Risk | Category | Likelihood | Impact | Mitigation | Residual risk | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| Prompt injection in customer dispute text | OWASP LLM01 / prompt injection | Medium | High | Guardrails validate input and quarantine untrusted text in [src/guardrails/io.py](src/guardrails/io.py) and [src/context/pipeline.py](src/context/pipeline.py) | Low | Project owner |
| Sensitive PAN/account leakage | Data exposure | Medium | High | Output sanitization, redaction, and suppression in [src/guardrails/io.py](src/guardrails/io.py) | Low | Project owner |
| Cross-session memory leakage | Data privacy / memory integrity | Low | Medium | SQLite-backed memory in [src/memory/manager.py](src/memory/manager.py) is scoped by case ID and kept synthetic | Low | Project owner |
| Tool or policy retrieval failure | Reliability / operational resilience | Medium | Medium | MCP server and RAG retrieval are surfaced through [mcp_server/server.py](mcp_server/server.py) and [src/tools/rag_tool.py](src/tools/rag_tool.py) with explicit status logging in [logs/tool_calls.jsonl](logs/tool_calls.jsonl) | Medium | Ops / engineering |
| Fraud or policy misclassification | Model and decisioning error | Medium | High | Decision logic, route checks, and escalation thresholds are separated in [src/agents/fraud_scorer.py](src/agents/fraud_scorer.py), [src/agents/resolution.py](src/agents/resolution.py), and [src/graph.py](src/graph.py) | Medium | Review team |

## Control citations
- Review gate: [src/agents/resolution.py](src/agents/resolution.py)
- Input validation: [src/guardrails/io.py](src/guardrails/io.py)
- Context quarantine: [src/context/pipeline.py](src/context/pipeline.py)
- Traceability: [src/observability/tracing.py](src/observability/tracing.py) and [traces/phoenix_export.jsonl](traces/phoenix_export.jsonl)
- Policy access: [mcp_server/server.py](mcp_server/server.py)
