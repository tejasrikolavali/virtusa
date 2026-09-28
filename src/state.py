from typing import Any, TypedDict
from pydantic import BaseModel, Field


class Dispute(BaseModel):
    dispute_id: str
    transaction_id: str
    customer_id: str
    amount: float
    currency: str = "USD"
    merchant: str
    transaction_status: str
    dispute_text: str
    prior_disputes: int = 0
    card_last4: str = "0000"
    country: str = "US"
    device_id: str | None = None
    channel: str = "web"
    customer_message: str | None = None
    risk_notes: list[str] = Field(default_factory=list)


class DisputeDecision(BaseModel):
    dispute_type: str
    fraud_score: float = Field(ge=0, le=100)
    recommended_action: str
    rationale: str
    cited_rules: list[str] = Field(default_factory=list)
    human_escalation: bool = False
    risk_tier: str = "low"


class FraudState(TypedDict, total=False):
    case_id: str
    dispute: dict[str, Any]
    dispute_type: str
    fraud_score: float
    risk_tier: str
    fraud_factors: list[str]
    retrieved_rules: list[dict[str, Any]]
    decision: dict[str, Any]
    human_escalation: bool
    rule_query: str
    messages: list[dict[str, str]]
    working_memory: list[dict[str, Any]]
    long_term_memory: list[dict[str, Any]]
    context_summary: str
    quarantined_text: dict[str, Any]
    route_history: list[str]
    retry_count: int
    step_count: int
    max_steps: int
    errors: list[str]
    status: str
    evidence: list[str]
    trace_run_id: str
    tool_activity: list[dict[str, Any]]
    mcp_status: str
    route: str
    compliance_notes: list[str]
