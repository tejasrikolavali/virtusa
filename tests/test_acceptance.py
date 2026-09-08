from src.fraud_copilot.graph.builder import run_case

def test_complete_acceptance_flow():
    result = run_case("data/orders/sample_orders.json", "ORDER-001")
    assert result["risk_tier"] == "HIGH"
    assert result["decision"] == "HOLD"
    assert result["reflection"]["ok"] is True
    assert result["quarantined_text"]["trusted"] is False
    assert result["retrieved_rules"]
