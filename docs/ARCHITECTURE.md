# Architecture
START -> Supervisor -> dispute classifier -> fraud scorer -> chargeback/RAG -> resolution
-> human escalation when required -> END.

Final implementation must add SQLite checkpointing, structured outputs at node
boundaries, MCP consumption via langchain-mcp-adapters, context/memory middleware,
Phoenix tracing, guardrails and audit middleware.
