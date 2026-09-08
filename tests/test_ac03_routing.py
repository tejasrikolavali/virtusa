from src.fraud_copilot.graph.builder import run_case

def test_ac03_routing():
    result = run_case("data/orders/sample_orders.json", "ORDER-001")
    assert result["risk_tier"] == "HIGH"
    assert result["decision"] == "HOLD"
    assert "escalation" in result["route_history"]
