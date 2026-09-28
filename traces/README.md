# Phoenix trace export

The repository persistently exports OpenTelemetry spans to JSONL so the trace data can be inspected without requiring a live Phoenix server.

- Export path: `traces/phoenix_spans.jsonl`
- Production code: `src/observability/tracing.py`
- Regenerate with: `python scripts/run_all_evidence.py`

