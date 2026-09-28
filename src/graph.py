from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

from src.agents.chargeback_rules import retrieve_rules
from src.agents.dispute_classifier import classify_dispute
from src.agents.fraud_scorer import score_fraud
from src.agents.resolution import resolve
from src.context.pipeline import (
    compress_context,
    select_context,
    write_context,
)
from src.guardrails.io import sanitize_output, validate_input
from src.observability.tracing import get_tracer, setup_phoenix
from src.state import FraudState
from src.tools.mcp_consumer import consume_mcp_context


# Initialize tracing once when the graph module is loaded.
setup_phoenix()
tracer = get_tracer()


def traced_node(
    name: str,
    fn: Callable[[FraudState], FraudState],
) -> Callable[[FraudState], FraudState]:
    """
    Wrap an actual LangGraph node in a real OpenTelemetry span.
    """

    def wrapped(state: FraudState) -> FraudState:
        case_id = str(
            state.get(
                "case_id",
                state.get("dispute", {}).get(
                    "dispute_id",
                    "UNKNOWN",
                ),
            )
        )

        with tracer.start_as_current_span(
            name,
            attributes={
                "agent.node": name,
                "component": "langgraph",
                "case_id": case_id,
            },
        ) as span:

            try:
                result = fn(state)

                span.set_attribute(
                    "agent.status",
                    "ok",
                )

                span.set_attribute(
                    "route.step_count",
                    int(
                        result.get(
                            "step_count",
                            state.get("step_count", 0),
                        )
                    ),
                )

                route = result.get(
                    "route_history",
                    [],
                )

                span.set_attribute(
                    "route.history",
                    " -> ".join(str(x) for x in route),
                )

                return result

            except Exception as exc:
                span.set_attribute(
                    "agent.status",
                    "error",
                )

                span.record_exception(exc)

                raise

    return wrapped


def prepare(state: FraudState) -> FraudState:
    """
    Supervisor/preparation node.

    Initializes state and obtains transaction context through
    the MCP context consumer.
    """

    state["route_history"] = (
        state.get("route_history", [])
        + ["supervisor"]
    )

    state["step_count"] = (
        int(state.get("step_count", 0))
        + 1
    )

    state["max_steps"] = int(
        state.get("max_steps", 12)
    )

    state["case_id"] = (
        state.get("case_id")
        or state.get(
            "dispute",
            {},
        ).get(
            "dispute_id",
            "UNKNOWN",
        )
    )

    state["dispute"] = (
        state.get("dispute")
        or {}
    )

    state["messages"] = (
        state.get("messages")
        or []
    )

    state["working_memory"] = (
        state.get("working_memory")
        or []
    )

    state["long_term_memory"] = (
        state.get("long_term_memory")
        or []
    )

    state["errors"] = (
        state.get("errors")
        or []
    )

    state["tool_activity"] = (
        state.get("tool_activity")
        or []
    )

    state["status"] = "prepared"

    if not state.get("case_id"):
        state["errors"].append(
            "Missing dispute identifier."
        )

    mcp_context = consume_mcp_context(
        state.get("dispute", {})
    )

    transaction_lookup = mcp_context.get(
        "transaction_lookup",
        {},
    )

    if transaction_lookup.get(
        "transaction_id"
    ):
        state["mcp_status"] = "ok"
    else:
        state["mcp_status"] = "unavailable"

    state["tool_activity"].append(
        {
            "tool_name": "mcp_context_fetch",
            "status": state["mcp_status"],
            "payload": mcp_context,
        }
    )

    return state


def supervisor_route(state: FraudState) -> str:
    """
    Conditional supervisor routing.

    The next worker is selected from the current state.
    """

    if (
        state.get("step_count", 0)
        > state.get("max_steps", 12)
    ):
        return "end"

    if not state.get("dispute_type"):
        return "classify"

    if state.get("fraud_score") is None:
        return "fraud"

    if not state.get("retrieved_rules"):
        return "rules"

    if not state.get("decision"):
        return "resolve"

    return "end"


def build_graph() -> Any:
    """
    Build the LangGraph workflow with checkpointing.
    """

    builder = StateGraph(FraudState)

    # Real traced nodes.
    builder.add_node(
        "prepare",
        traced_node(
            "supervisor",
            prepare,
        ),
    )

    builder.add_node(
        "dispute_classifier",
        traced_node(
            "dispute_classifier",
            classify_dispute,
        ),
    )

    builder.add_node(
        "fraud_scorer",
        traced_node(
            "fraud_scorer",
            score_fraud,
        ),
    )

    builder.add_node(
        "chargeback_rules",
        traced_node(
            "chargeback_rules",
            retrieve_rules,
        ),
    )

    builder.add_node(
        "resolution",
        traced_node(
            "resolution",
            resolve,
        ),
    )

    builder.add_node(
        "write_context",
        traced_node(
            "write_context",
            write_context,
        ),
    )

    builder.add_node(
        "select_context",
        traced_node(
            "select_context",
            select_context,
        ),
    )

    builder.add_node(
        "compress_context",
        traced_node(
            "compress_context",
            compress_context,
        ),
    )

    # Entry point.
    builder.add_edge(
        START,
        "prepare",
    )

    # State-driven supervisor routing.
    builder.add_conditional_edges(
        "prepare",
        supervisor_route,
        {
            "classify": "dispute_classifier",
            "fraud": "fraud_scorer",
            "rules": "chargeback_rules",
            "resolve": "resolution",
            "end": END,
        },
    )

    # Context engineering flow.
    builder.add_edge(
        "dispute_classifier",
        "write_context",
    )

    builder.add_edge(
        "write_context",
        "select_context",
    )

    builder.add_edge(
        "select_context",
        "fraud_scorer",
    )

    # Risk and rules.
    builder.add_edge(
        "fraud_scorer",
        "chargeback_rules",
    )

    # Resolution.
    builder.add_edge(
        "chargeback_rules",
        "resolution",
    )

    # Compression/finalization.
    builder.add_edge(
        "resolution",
        "compress_context",
    )

    builder.add_edge(
        "compress_context",
        END,
    )

    # SQLite checkpointing.
    db_path = (
        Path(__file__).resolve().parent.parent
        / "logs"
        / "graph_checkpoint.sqlite"
    )

    db_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    import sqlite3

    conn = sqlite3.connect(
        db_path,
        check_same_thread=False,
    )

    checkpoint = SqliteSaver(conn)

    return builder.compile(
        checkpointer=checkpoint
    )


graph = build_graph()


def process_dispute(
    payload: dict[str, Any],
) -> dict[str, Any]:
    """
    Process one synthetic dispute through the LangGraph workflow.
    """

    validate_input(payload)

    case_id = payload.get(
        "dispute_id",
        "UNKNOWN",
    )

    with tracer.start_as_current_span(
        "process_dispute",
        attributes={
            "component": "copilot",
            "workflow": "transaction-dispute-fraud-triage",
            "case_id": str(case_id),
        },
    ) as span:

        state: FraudState = {
            "case_id": case_id,
            "dispute": payload,
            "route_history": [],
            "step_count": 0,
            "max_steps": 12,
            "messages": [
                {
                    "role": "user",
                    "content": payload.get(
                        "dispute_text",
                        "",
                    ),
                }
            ],
            "working_memory": [],
            "long_term_memory": [],
            "errors": [],
            "tool_activity": [],
            "status": "new",
        }

        try:
            result = graph.invoke(
                state,
                config={
                    "configurable": {
                        "thread_id": case_id,
                    }
                },
            )

            result["decision"] = sanitize_output(
                result.get(
                    "decision",
                    {},
                )
            )

            span.set_attribute(
                "workflow.status",
                "ok",
            )

            span.set_attribute(
                "workflow.decision",
                str(
                    result.get(
                        "decision",
                        {},
                    ).get(
                        "recommended_action",
                        "unknown",
                    )
                ),
            )

            span.set_attribute(
                "workflow.route",
                " -> ".join(
                    str(x)
                    for x in result.get(
                        "route_history",
                        [],
                    )
                ),
            )

            return result

        except Exception as exc:
            span.set_attribute(
                "workflow.status",
                "error",
            )

            span.record_exception(exc)

            raise