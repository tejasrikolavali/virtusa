from src.fraud_copilot.graph.builder import pause_case, resume_case, run_case
from src.fraud_copilot.config import settings

def test_ac05_checkpoint():
    case_id = "CASE-ORDER-001-PAUSE-TEST"
    paused = pause_case("data/orders/sample_orders.json", "ORDER-001", case_id=case_id)
    assert paused["case_id"] == case_id
    assert "risk_score" not in paused

    resumed = resume_case(case_id)
    assert resumed["decision"] == "HOLD"
    assert resumed["route_history"][-1] == "finalize"

    result = run_case(
        "data/orders/sample_orders.json",
        "ORDER-001",
        pause_before="risk_scoring",
    )
    assert result["case_id"] == "CASE-ORDER-001"
    assert settings.checkpoint_db.exists()
    assert result["decision"] == "HOLD"
    assert result["route_history"][-1] == "finalize"
