from src.fraud_copilot.reflection.self_healing import reflect

def test_ac12_reflection():
    ok = reflect({"risk_score": 80, "risk_tier": "HIGH", "decision": "HOLD", "retry_count": 0})
    assert ok["ok"] is True

    bad = reflect({"risk_score": 200, "risk_tier": "HIGH", "decision": "HOLD", "retry_count": 0})
    assert bad["action"] == "RETRY"

    malformed = reflect({"risk_score": None, "risk_tier": "HIGH", "decision": "HOLD"})
    assert malformed["action"] == "RETRY"
