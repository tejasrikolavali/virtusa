from src.fraud_copilot.graph.builder import run_case
from src.fraud_copilot.verification import rag_check


def test_ac11_low_risk_can_skip_rag():
    result = run_case("data/orders/sample_orders.json", "ORDER-002")
    assert result["rag_decision"]["agent_decided_to_call"] is False
    assert result["retrieved_rules"] == []
    assert rag_check(result) is True