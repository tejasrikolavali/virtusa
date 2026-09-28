from scripts.run_all_evidence import generate_eval_report, generate_golden_signals


def test_equivalent_local_eval_report_is_not_null_without_gemini(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    results = [
        {
            "case_id": "DISP-001",
            "fraud_score": 81,
            "dispute_type": "unauthorized_transaction",
            "decision": {
                "recommended_action": "investigate",
                "rationale": "High-risk transaction requires review.",
                "cited_rules": ["R-401"],
            },
            "route_history": ["supervisor", "classify", "fraud", "rules", "resolve"],
            "status": "resolved",
            "latency_ms": 15.2,
        },
        {
            "case_id": "DISP-002",
            "fraud_score": 42,
            "dispute_type": "duplicate_transaction",
            "decision": {
                "recommended_action": "deny",
                "rationale": "Charge matches a prior duplicate transaction.",
                "cited_rules": ["R-220"],
            },
            "route_history": ["supervisor", "classify", "fraud", "rules", "resolve"],
            "status": "resolved",
            "latency_ms": 18.4,
        },
    ]

    report = generate_eval_report(results)
    metrics = report["metrics"]

    for key in ("accuracy", "hallucination_rate", "faithfulness", "relevance"):
        assert metrics[key] is not None
        assert isinstance(metrics[key], (int, float))


def test_golden_signals_propagate_eval_metrics_without_fabricating_cost():
    results = [
        {
            "case_id": "DISP-001",
            "fraud_score": 81,
            "dispute_type": "unauthorized_transaction",
            "decision": {"recommended_action": "investigate"},
            "route_history": ["supervisor", "classify", "fraud", "rules", "resolve"],
            "status": "resolved",
            "latency_ms": 15.2,
        },
        {
            "case_id": "DISP-002",
            "fraud_score": 42,
            "dispute_type": "duplicate_transaction",
            "decision": {"recommended_action": "deny"},
            "route_history": ["supervisor", "classify", "fraud", "rules", "resolve"],
            "status": "resolved",
            "latency_ms": 18.4,
        },
    ]

    eval_report = {
        "metrics": {
            "cases_executed": 2,
            "successful_cases": 2,
            "execution_success_rate": 1.0,
            "accuracy": 1.0,
            "hallucination_rate": 0.0,
            "faithfulness": 1.0,
            "relevance": 1.0,
        }
    }

    payload = generate_golden_signals(results, eval_report)

    assert payload["source"]["tracing"] == "traces/phoenix_spans.jsonl"
    assert payload["metrics"]["accuracy"] == 1.0
    assert payload["metrics"]["hallucination_rate"] == 0.0
    assert payload["metrics"]["faithfulness"] == 1.0
    assert payload["metrics"]["relevance"] == 1.0
    assert payload["metrics"]["estimated_cost_usd"] is None
    assert "No synthetic cost is inserted" in payload["metrics"]["cost_note"]
