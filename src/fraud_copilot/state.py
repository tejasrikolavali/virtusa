from typing import Any, TypedDict

class FraudState(TypedDict, total=False):
    case_id: str
    order: dict[str, Any]
    signals: list[dict[str, Any]]
    risk_score: float
    risk_tier: str
    retrieved_rules: list[dict[str, Any]]
    rag_decision: dict[str, Any]
    decision: str
    resolution: dict[str, Any]
    escalation: dict[str, Any]
    messages: list[dict[str, Any]]
    working_memory: list[dict[str, Any]]
    long_term_memory: list[dict[str, Any]]
    quarantined_text: dict[str, Any]
    context_summary: str
    errors: list[str]
    retry_count: int
    reflection: dict[str, Any]
    route_history: list[str]
    mcp_transcript: list[dict[str, Any]]
