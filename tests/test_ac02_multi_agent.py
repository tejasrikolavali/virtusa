from src.fraud_copilot.graph.builder import build_graph

def test_ac02_multi_agent():
    graph = build_graph()
    nodes = set(graph.nodes.keys())
    assert {"signal_collection", "risk_scoring", "resolution_draft", "escalation"} <= nodes
