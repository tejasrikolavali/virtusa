from src.fraud_copilot.agents.signal_agent import collect_signals
from src.fraud_copilot.agents.risk_agent import score_risk
from src.fraud_copilot.agents.resolution_agent import draft_resolution
from pydantic import BaseModel

def test_ac04_structured_output():
    s = collect_signals({"payment_status": "verified", "billing_shipping_match": False})
    r = score_risk(s.signals)
    d = draft_resolution(r.risk_tier, r.reasons)
    assert isinstance(s, BaseModel)
    assert isinstance(r, BaseModel)
    assert isinstance(d, BaseModel)
