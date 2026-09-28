import importlib

from src.observability import tracing as tracing_module


def test_setup_phoenix_uses_local_jsonl_span_export(monkeypatch):
    monkeypatch.setenv("PHOENIX_COLLECTOR_ENDPOINT", "http://127.0.0.1:1")
    monkeypatch.setenv("PHOENIX_PROJECT_NAME", "transaction-dispute-fraud-triage")

    trace_module = importlib.reload(tracing_module)
    result = trace_module.setup_phoenix()

    assert result["status"] in {"phoenix_registered", "local_fallback", "already_initialized"}
    assert trace_module.TRACE_FILE.name == "phoenix_spans.jsonl"

    tracer = trace_module.get_tracer()
    with tracer.start_as_current_span("test_span") as span:
        span.set_attribute("component", "test")
        span.set_attribute("case_id", "CASE-TRACE-01")

    assert trace_module.TRACE_FILE.exists()
    lines = trace_module.TRACE_FILE.read_text(encoding="utf-8").splitlines()
    assert lines

    payload = lines[-1]
    assert "trace_id" in payload
    assert "span_id" in payload
    assert "status" in payload
    assert "test_span" in payload
