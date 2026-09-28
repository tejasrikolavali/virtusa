from src.graph import supervisor_route


def test_step_limit_stops_cascade():
    assert supervisor_route({"step_count": 13, "max_steps": 12}) == "end"


def test_step_limit_is_respected_when_routing_loop_detected():
    state = {"step_count": 12, "max_steps": 12, "dispute_type": "merchant_dispute", "fraud_score": 20, "retrieved_rules": []}
    assert supervisor_route(state) == "rules"


def test_invalid_state_does_not_loop_forever():
    state = {"step_count": 40, "max_steps": 12, "dispute_type": "unauthorized_transaction", "fraud_score": 50, "retrieved_rules": [{"rule_id": "X"}]}
    assert supervisor_route(state) == "end"
