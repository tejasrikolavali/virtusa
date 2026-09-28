from src.graph import process_dispute, supervisor_route


def test_routes_to_classifier_first():
    assert supervisor_route({"step_count": 0, "max_steps": 12}) == "classify"


def test_routes_to_fraud_after_classification():
    assert supervisor_route({"dispute_type": "unauthorized_transaction", "step_count": 1, "max_steps": 12}) == "fraud"


def test_routes_to_rules_after_fraud_score():
    assert supervisor_route({"dispute_type": "merchant_dispute", "fraud_score": 42, "step_count": 2, "max_steps": 12}) == "rules"


def test_end_to_end_process_runs_for_sample_case():
    sample = {
        "dispute_id": "DISP-TEST",
        "transaction_id": "TXN-TEST",
        "customer_id": "CUSTOMER-TEST",
        "amount": 150.0,
        "currency": "USD",
        "merchant": "Corner Cafe",
        "transaction_status": "posted",
        "dispute_text": "I did not recognize this coffee purchase.",
        "prior_disputes": 0,
        "card_last4": "4242",
        "country": "US",
        "device_id": "DEV-TEST-1",
        "channel": "mobile",
    }
    result = process_dispute(sample)
    assert result["dispute_type"]
    assert result["decision"]["recommended_action"] in {"investigate", "provisional_credit", "deny"}
