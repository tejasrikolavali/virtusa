import json
from pathlib import Path

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from ..state import FraudState
from ..schemas import OrderInput
from ..config import settings
from .nodes import (
    prepare_node, signal_node, risk_node, resolution_node,
    escalation_node, reflection_node, finalize_node
)
from ..agents.supervisor import reflection_route, supervisor_route

def build_graph():
    graph = StateGraph(FraudState)
    graph.add_node("prepare", prepare_node)
    graph.add_node("signal_collection", signal_node)
    graph.add_node("risk_scoring", risk_node)
    graph.add_node("resolution_draft", resolution_node)
    graph.add_node("escalation", escalation_node)
    graph.add_node("reflection", reflection_node)
    graph.add_node("finalize", finalize_node)

    graph.add_edge(START, "prepare")
    graph.add_conditional_edges(
        "prepare",
        supervisor_route,
        {
            "signal": "signal_collection",
            "risk": "risk_scoring",
            "resolution": "resolution_draft",
            "escalation": "escalation",
            "done": "finalize",
        },
    )
    graph.add_edge("signal_collection", "risk_scoring")

    # Explicit conditional edge driven by state.
    graph.add_conditional_edges(
        "risk_scoring",
        lambda state: "resolution_draft" if state.get("risk_tier") in {"LOW", "MEDIUM", "HIGH"} else "reflection",
        {"resolution_draft": "resolution_draft", "reflection": "reflection"},
    )

    graph.add_conditional_edges(
        "resolution_draft",
        lambda state: "escalation" if state.get("risk_tier") == "HIGH" else "reflection",
        {"escalation": "escalation", "reflection": "reflection"},
    )
    graph.add_edge("escalation", "reflection")
    graph.add_conditional_edges(
        "reflection",
        reflection_route,
        {"retry": "risk_scoring", "finalize": "finalize"},
    )
    graph.add_edge("finalize", END)

    return graph

def _load_order(path, order_id):
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Order file not found: {source}")
    data = json.loads(source.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("orders", [data])
    if not isinstance(data, list):
        raise ValueError("Order input must be an object or an orders list")
    for order in data:
        if order.get("order_id") == order_id:
            return OrderInput.model_validate(order).model_dump()
    raise ValueError(f"Order {order_id} not found")

def _initial_state(order: dict, case_id: str) -> FraudState:
    return {
        "case_id": case_id,
        "order": order,
        "signals": [],
        "messages": [],
        "errors": [],
        "retry_count": 0,
        "route_history": [],
    }

def pause_case(order_path, order_id="ORDER-001", pause_before="risk_scoring", case_id=None):
    """Run until an interrupt and return the persisted state for later resume."""
    order = _load_order(order_path, order_id)
    case_id = case_id or f"CASE-{order_id}"
    with SqliteSaver.from_conn_string(str(settings.checkpoint_db)) as checkpointer:
        checkpointer.delete_thread(case_id)
        compiled = build_graph().compile(
            checkpointer=checkpointer,
            interrupt_before=[pause_before],
        )
        config = {"configurable": {"thread_id": case_id}}
        compiled.invoke(_initial_state(order, case_id), config=config)
        snapshot = compiled.get_state(config)
        if not snapshot.next:
            raise RuntimeError(f"Graph did not pause before {pause_before}")
        return snapshot.values

def resume_case(case_id):
    """Resume a previously interrupted case using its SQLite checkpoint."""
    with SqliteSaver.from_conn_string(str(settings.checkpoint_db)) as checkpointer:
        compiled = build_graph().compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": case_id}}
        snapshot = compiled.get_state(config)
        if not snapshot.next:
            raise ValueError(f"No paused checkpoint found for {case_id}")
        return compiled.invoke(None, config=config)

def run_case(order_path, order_id="ORDER-001", pause_before=None):
    order = _load_order(order_path, order_id)
    case_id = f"CASE-{order_id}"

    # Checkpointing is configured with SQLite.
    with SqliteSaver.from_conn_string(str(settings.checkpoint_db)) as checkpointer:
        compile_options = {}
        if pause_before:
            compile_options["interrupt_before"] = [pause_before]
        compiled = build_graph().compile(checkpointer=checkpointer, **compile_options)
        config = {"configurable": {"thread_id": case_id}}
        result = compiled.invoke(_initial_state(order, case_id), config=config)
        if pause_before:
            snapshot = compiled.get_state(config)
            if snapshot.next:
                result = resume_case(case_id)
    return result
