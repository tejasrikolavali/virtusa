from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult
from phoenix.otel import register as register_phoenix


TRACE_DIR = Path(__file__).resolve().parents[2] / "traces"
TRACE_FILE = TRACE_DIR / "phoenix_spans.jsonl"

_provider: TracerProvider | None = None
_tracer = None
_langchain_instrumented = False
_setup_error: Exception | None = None
_local_exporter_attached = False


def _is_sensitive_key(key: str) -> bool:
    lowered = str(key).lower()
    return any(token in lowered for token in [
        "pan",
        "account",
        "card",
        "secret",
        "token",
        "password",
        "customer_text",
        "dispute_text",
        "raw_text",
        "prompt",
    ])


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, str):
        sanitized = value
        sanitized = re.sub(r"\b\d{13,19}\b", "[REDACTED_PAN]", sanitized)
        sanitized = re.sub(r"\b\d{8,12}\b", "[REDACTED_ACCOUNT]", sanitized)
        if any(marker in sanitized.lower() for marker in [
            "ignore previous instructions",
            "reveal another customer",
            "show me the full card",
            "override rules",
            "bypass fraud",
        ]):
            sanitized = "[REDACTED_UNTRUSTED_TEXT]"
        return sanitized[:2000]
    if isinstance(value, dict):
        return {str(key): _sanitize_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_sanitize_value(item) for item in value]
    return value


class JsonlSpanExporter(SpanExporter):
    """Write committed OpenTelemetry span evidence for Phoenix-compatible local review."""

    def export(self, spans) -> SpanExportResult:
        TRACE_DIR.mkdir(parents=True, exist_ok=True)

        with TRACE_FILE.open("a", encoding="utf-8") as handle:
            for span in spans:
                context = span.get_span_context()
                trace_id = format(context.trace_id, "032x")
                span_id = format(context.span_id, "016x")
                parent_span_id = None
                if span.parent:
                    parent_span_id = format(span.parent.span_id, "016x")

                start_ns = span.start_time or 0
                end_ns = span.end_time or start_ns
                latency_ms = round((end_ns - start_ns) / 1_000_000, 3)

                attributes: dict[str, Any] = {}
                for key, value in span.attributes.items():
                    if _is_sensitive_key(str(key)):
                        continue
                    attributes[str(key)] = _sanitize_value(value)

                events = []
                for event in span.events:
                    event_payload = {}
                    for key, value in (event.attributes or {}).items():
                        if _is_sensitive_key(str(key)):
                            continue
                        event_payload[str(key)] = _sanitize_value(value)
                    events.append({"name": event.name, "attributes": event_payload})

                record = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "trace_id": trace_id,
                    "run_id": trace_id,
                    "span_id": span_id,
                    "parent_span_id": parent_span_id,
                    "name": span.name,
                    "start_time_unix_ns": start_ns,
                    "end_time_unix_ns": end_ns,
                    "latency_ms": latency_ms,
                    "status": span.status.status_code.name,
                    "attributes": attributes,
                    "events": events,
                }

                handle.write(json.dumps(record, default=str, ensure_ascii=False) + "\n")

        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        return None

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True


def setup_phoenix() -> dict[str, Any]:
    """Register Phoenix with the installed OTel API and keep a local JSONL exporter for committed evidence."""
    global _provider, _tracer, _setup_error, _langchain_instrumented, _local_exporter_attached

    if _provider is not None:
        return {
            "enabled": True,
            "status": "already_initialized",
            "project_name": os.getenv("PHOENIX_PROJECT_NAME", "transaction-dispute-fraud-triage"),
            "collector_endpoint": os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://127.0.0.1:6006"),
            "tracer": "transaction-dispute-fraud-triage",
            "setup_error": str(_setup_error) if _setup_error else None,
        }

    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    collector_endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://127.0.0.1:6006")
    project_name = os.getenv("PHOENIX_PROJECT_NAME", "transaction-dispute-fraud-triage")
    registration_status = "phoenix_registered"
    _setup_error = None

    try:
        _provider = register_phoenix(
            endpoint=collector_endpoint,
            project_name=project_name,
            batch=False,
            set_global_tracer_provider=True,
            auto_instrument=False,
            verbose=False,
        )
    except Exception as exc:  # pragma: no cover - exercised by environment fallback test
        _setup_error = exc
        registration_status = "local_fallback"
        _provider = TracerProvider()
        trace.set_tracer_provider(_provider)

    if not _local_exporter_attached:
        _provider.add_span_processor(SimpleSpanProcessor(JsonlSpanExporter()))
        _local_exporter_attached = True

    _tracer = _provider.get_tracer("transaction-dispute-fraud-triage")

    if not _langchain_instrumented:
        try:
            LangChainInstrumentor().instrument()
            _langchain_instrumented = True
        except Exception as exc:
            _setup_error = exc

    return {
        "enabled": True,
        "status": registration_status,
        "project_name": project_name,
        "collector_endpoint": collector_endpoint,
        "tracer": "transaction-dispute-fraud-triage",
        "setup_error": str(_setup_error) if _setup_error else None,
    }


def get_tracer():
    global _tracer
    if _tracer is None:
        setup_phoenix()
    return _tracer


def flush_traces() -> None:
    if _provider is not None:
        try:
            _provider.force_flush()
        except Exception:
            pass