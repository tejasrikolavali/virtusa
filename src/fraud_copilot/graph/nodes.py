import json
from pathlib import Path

from ..agents.signal_agent import collect_signals
from ..agents.risk_agent import score_risk
from ..agents.resolution_agent import draft_resolution
from ..agents.escalation_agent import create_escalation
from ..agents.supervisor import supervisor_route
from ..mcp.client import run_mcp_tools
from ..context.quarantine import quarantine_order_text
from ..context.writer import write_context
from ..context.selector import select_context
from ..context.compressor import compress_messages
from ..memory.manager import TieredMemory
from ..reflection.self_healing import reflect
from ..rag.retriever import FraudRuleRetriever
from ..config import settings

memory = TieredMemory(settings.index_dir / "memory.sqlite", settings.index_dir / "semantic_memory")

def log_event(case_id, event, payload):
    p = settings.logs_dir / "agent_runs" / f"{case_id}.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"case_id": case_id, "event": event, "payload": payload}, default=str) + "\n")

def prepare_node(state):
    order = state["order"]
    q = quarantine_order_text(order)
    ctx = write_context(state)
    memory.remember(state["case_id"], f"Order {order.get('order_id')} received.", importance=7)
    state["quarantined_text"] = q
    state["working_memory"] = memory.working.get(state["case_id"], [])
    state["long_term_memory"] = memory.recall(state["case_id"])
    state["messages"] = state.get("messages", []) + [
        {"role": "system", "content": "Prepared trusted case context."}
    ]
    state["messages"], state["context_summary"] = compress_messages(
        state["messages"]
    )
    state["mcp_transcript"] = run_mcp_tools(order.get("order_id", ""))
    state["route_history"] = ["supervisor"]
    log_event(state["case_id"], "context_prepared", {
        "quarantine": q,
        "context": ctx,
        "mcp_transcript": state["mcp_transcript"],
        "context_summary": state["context_summary"],
    })
    return state

def signal_node(state):
    out = collect_signals(state["order"])
    state["signals"] = out.model_dump()["signals"]
    state["route_history"].append("signal_collection")
    log_event(state["case_id"], "signal_collection", out.model_dump())
    return state

def risk_node(state):
    out = score_risk(state.get("signals", []))
    state["risk_score"] = out.risk_score
    state["risk_tier"] = out.risk_tier
    state["messages"].append({"role": "assistant", "content": f"Risk score {out.risk_score}."})
    state["route_history"].append("risk_scoring")

    # Agentic-RAG decision: this node decides whether policy lookup is useful.
    should_retrieve = out.risk_tier in {"MEDIUM", "HIGH"} or bool(state.get("signals"))
    state["rag_decision"] = {
        "agent_decided_to_call": should_retrieve,
        "reason": "Risk signals require policy grounding." if should_retrieve else "No policy lookup needed.",
    }
    if should_retrieve:
        retriever = FraudRuleRetriever(settings.data_dir / "knowledge")
        query = " ".join(out.reasons + ["fraud rule chargeback"])
        state["retrieved_rules"] = retriever.search(query)
    else:
        state["retrieved_rules"] = []
    log_event(state["case_id"], "risk_and_agentic_rag", {
        "risk": out.model_dump(),
        "rag_decision": state["rag_decision"],
        "retrieved_rules": state["retrieved_rules"],
    })
    return state

def resolution_node(state):
    selected = select_context(state, "resolution")
    out = draft_resolution(state["risk_tier"], [s["name"] for s in state.get("signals", [])])
    state["decision"] = out.decision
    state["resolution"] = out.model_dump()
    state["route_history"].append("resolution_draft")
    log_event(state["case_id"], "resolution", {"selected_context": selected, "output": out.model_dump()})
    return state

def escalation_node(state):
    out = create_escalation(state["risk_tier"], [s["name"] for s in state.get("signals", [])])
    state["escalation"] = out.model_dump()
    state["route_history"].append("escalation")
    log_event(state["case_id"], "escalation", out.model_dump())
    return state

def reflection_node(state):
    state["reflection"] = reflect(state)
    state["retry_count"] = state["reflection"].get(
        "next_retry_count", state.get("retry_count", 0)
    )
    state["route_history"].append("reflection")
    log_event(state["case_id"], "reflection", state["reflection"])
    return state

def finalize_node(state):
    state["long_term_memory"] = memory.recall(state["case_id"])
    state["working_memory"] = memory.working.get(state["case_id"], [])
    state["route_history"].append("finalize")
    memory.evict(max_items=50)
    log_event(state["case_id"], "finalize", {
        "decision": state.get("decision"),
        "risk_tier": state.get("risk_tier"),
        "routes": state.get("route_history"),
    })
    return state
