from __future__ import annotations

import time
from typing import Any

from src.observability.tool_logging import log_tool_call
from src.observability.tracing import get_tracer, setup_phoenix


setup_phoenix()
tracer = get_tracer()


def _synthetic_transaction_snapshot(
    dispute: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the synthetic transaction snapshot used by the
    local MCP-compatible context flow.
    """

    txn_id = dispute.get(
        "transaction_id",
        "TXN-UNKNOWN",
    )

    return {
        "transaction_id": txn_id,
        "customer_id": dispute.get(
            "customer_id",
            "CUSTOMER-UNKNOWN",
        ),
        "amount": float(
            dispute.get(
                "amount",
                0,
            )
            or 0
        ),
        "currency": dispute.get(
            "currency",
            "USD",
        ),
        "merchant": dispute.get(
            "merchant",
            "UNKNOWN",
        ),
        "status": dispute.get(
            "transaction_status",
            "posted",
        ),
        "card_last4": dispute.get(
            "card_last4",
            "0000",
        ),
    }


def consume_mcp_context(
    dispute: dict[str, Any],
) -> dict[str, Any]:
    """
    Consume transaction context and record a real tool span.

    The tool log remains the detailed machine-readable audit trail,
    while OpenTelemetry records the execution span and timing.
    """

    started = time.perf_counter()

    case_id = str(
        dispute.get(
            "dispute_id",
            "UNKNOWN",
        )
    )

    transaction_id = str(
        dispute.get(
            "transaction_id",
            "TXN-UNKNOWN",
        )
    )

    with tracer.start_as_current_span(
        "mcp_context_fetch",
        attributes={
            "component": "mcp",
            "tool.name": "mcp_context_fetch",
            "tool.protocol": "MCP",
            "case_id": case_id,
            "transaction_id": transaction_id,
        },
    ) as span:

        try:
            txn = _synthetic_transaction_snapshot(
                dispute
            )

            prior = [
                {
                    "customer_id": dispute.get(
                        "customer_id"
                    ),
                    "dispute_id": dispute.get(
                        "dispute_id"
                    ),
                    "amount": float(
                        dispute.get(
                            "amount",
                            0,
                        )
                        or 0
                    ),
                    "status": "reviewed",
                }
            ]

            payload = {
                "transaction_lookup": txn,
                "prior_disputes": prior,
                "resource": "policy://chargeback-rules",
            }

            span.set_attribute(
                "tool.status",
                "ok",
            )

            span.set_attribute(
                "tool.resource",
                "policy://chargeback-rules",
            )

            log_tool_call(
                "agent",
                "mcp_context_fetch",
                {
                    "transaction_id": txn[
                        "transaction_id"
                    ],
                    "customer_id": txn[
                        "customer_id"
                    ],
                },
                payload,
                started,
                status="ok",
            )

            return payload

        except Exception as exc:
            span.set_attribute(
                "tool.status",
                "error",
            )

            span.record_exception(exc)

            log_tool_call(
                "agent",
                "mcp_context_fetch",
                {
                    "transaction_id": transaction_id,
                    "customer_id": dispute.get(
                        "customer_id"
                    ),
                },
                {
                    "error": str(exc)
                },
                started,
                status="error",
            )

            return {
                "transaction_lookup": {
                    "error": "MCP context unavailable"
                },
                "prior_disputes": [],
                "resource": "policy://chargeback-rules",
            }