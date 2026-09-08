from src.fraud_copilot.state import FraudState
from src.fraud_copilot.graph.builder import build_graph

def test_ac01_typed_state():
    assert FraudState is not None
    graph = build_graph()
    assert graph is not None
