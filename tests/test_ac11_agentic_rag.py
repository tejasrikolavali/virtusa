from src.fraud_copilot.graph.builder import run_case

def test_ac11_agentic_rag():
    result = run_case("data/orders/sample_orders.json", "ORDER-001")
    assert result["rag_decision"]["agent_decided_to_call"] is True
    assert result["retrieved_rules"]
