from typing import Literal
from pydantic import BaseModel, Field

class OrderInput(BaseModel):
    order_id: str = Field(min_length=1)
    payment_status: str = Field(min_length=1)
    amount: float = Field(ge=0)
    billing_shipping_match: bool
    velocity_24h: int = Field(ge=0)
    device_new: bool
    customer_free_text: str = ""
    order_free_text: str = ""

    model_config = {"extra": "allow"}

class SignalOutput(BaseModel):
    signals: list[dict] = Field(default_factory=list)
    source: str = "synthetic"

class RiskScoreOutput(BaseModel):
    risk_score: float = Field(ge=0, le=100)
    risk_tier: Literal["LOW", "MEDIUM", "HIGH"]
    reasons: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)

class ResolutionOutput(BaseModel):
    decision: Literal["RELEASE", "REVIEW", "HOLD"]
    rationale: str
    customer_safe_note: str

class EscalationOutput(BaseModel):
    required: bool
    priority: Literal["LOW", "MEDIUM", "HIGH"]
    reason: str
