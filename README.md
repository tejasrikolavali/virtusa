# Order Fraud & Chargeback Triage Copilot

Business Case: AAIE_AGT_026_ECM  
Domain: E-commerce — Payments Risk  
Track: Agentic AI Core + Context Engineering & Memory + MCP & Interoperability

This repository implements the mandatory requirements in the supplied capstone case study:

- LangGraph typed state
- Supervisor + signal, risk, resolution and escalation workers
- Conditional state-driven routing
- Pydantic structured outputs
- SQLite checkpointing for pause/resume
- Tiered short-term + persistent long-term memory
- Cross-session memory persistence test
- Importance-based memory eviction
- Custom MCP server with 2 tools + 1 resource
- MCP consumption through langchain-mcp-adapters
- Agentic RAG for fraud rules and chargeback reasons
- Context write/select/compress/isolate
- Untrusted free-text quarantine
- Reflection/self-healing loop
- Synthetic data only
- Structured JSON evidence
- CLI
- AC-01 to AC-12 tests and evidence

## Quick start

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Put your Google Gemini API key in `.env`.

Run the demo:

```powershell
python -m app.cli demo
```

Run the acceptance suite:

```powershell
python -m pytest -q
```

Run the final audit:

```powershell
python scripts/audit_project.py
```

Run individual evidence demonstrations:

```powershell
python scripts/run_memory_test.py
python scripts/run_mcp_demo.py
python scripts/run_rag_demo.py
streamlit run app/streamlit_app.py
```

## Important

The case study requires Google Gemini as the only model provider. Do not add Groq, OpenAI, Anthropic, real payment gateways, real customer data, Docker, or external databases.

The application uses deterministic synthetic fallbacks when `GOOGLE_API_KEY` is not available, so the engineering tests can still validate graph, memory, MCP, RAG, checkpoint, routing and evidence behavior. The LLM provider remains Google Gemini.

## Repository map

- `src/fraud_copilot/state.py` — typed graph state
- `src/fraud_copilot/schemas.py` — Pydantic handoff schemas
- `src/fraud_copilot/graph/` — LangGraph graph, nodes and conditional routing
- `src/fraud_copilot/agents/` — specialized worker agents
- `src/fraud_copilot/context/` — write/select/compress/isolate
- `src/fraud_copilot/memory/` — tiered memory and eviction
- `src/fraud_copilot/rag/` — semantic fraud-rule/chargeback retrieval
- `src/fraud_copilot/mcp/` — MCP adapter client
- `mcp_server/` — custom MCP server
- `tests/` — AC-01 through AC-12
- `evidence/` — committed AC evidence
- `logs/` — committed structured run traces
- `docs/` — requirement/rationale documents

Checkpoint pause/resume is available through `pause_case()` and `resume_case()`
in `src/fraud_copilot.graph.builder`; `run_case()` remains the one-call demo
that resumes automatically.


## Sample run

```powershell
python -m app.cli run --order data/orders/sample_orders.json --order-id ORDER-001
```

The CLI prints the risk score, risk tier, routing, RAG decision, MCP signals, memory information, reflection result and final resolution.

## Reproducibility

The project is designed to run with pip + Python only. No Docker or external database service is required.
