import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.fraud_copilot.config import settings
from src.fraud_copilot.graph.builder import run_case
from src.fraud_copilot.verification import rag_check


DEFAULT_ORDER_PATH = ROOT / "data" / "orders" / "sample_orders.json"


def _available_order_ids(order_path):
    try:
        data = json.loads(Path(order_path).read_text(encoding="utf-8"))
        orders = data.get("orders", [data]) if isinstance(data, dict) else data
        return [order["order_id"] for order in orders if order.get("order_id")]
    except (OSError, json.JSONDecodeError, TypeError, KeyError):
        return []


def _status(value):
    return "PASS" if value else "FAIL"


def _verification(result):
    reflection = result.get("reflection", {})
    transcript = result.get("mcp_transcript", [])
    return {
        "AC-01": bool(result.get("case_id")),
        "AC-02": {"signal_collection", "risk_scoring", "resolution_draft"}.issubset(
            set(result.get("route_history", []))
        ),
        "AC-03": result.get("risk_tier") in {"LOW", "MEDIUM", "HIGH"},
        "AC-04": bool(result.get("resolution")),
        "AC-05": settings.checkpoint_db.exists(),
        "AC-06": "working_memory" in result and "long_term_memory" in result,
        "AC-07": bool(result.get("long_term_memory")),
        "AC-08": settings.index_dir.exists(),
        "AC-09": len(transcript) >= 2,
        "AC-10": all(item.get("status") == "success" for item in transcript),
        "AC-11": rag_check(result),
        "AC-12": reflection.get("action") in {"CONTINUE", "STOP_WITH_EXPLICIT_FAILURE"},
    }


st.set_page_config(page_title="Order Fraud Copilot", layout="wide")
st.title("Order Fraud & Chargeback Triage Copilot")
st.caption("Synthetic case execution and acceptance verification")

with st.sidebar:
    st.header("Case input")
    order_path = st.text_input("Order JSON", str(DEFAULT_ORDER_PATH))
    order_ids = _available_order_ids(order_path)
    if order_ids:
        order_id = st.selectbox("Sample order", order_ids)
    else:
        st.error("No valid orders found in the selected JSON file.")
        order_id = None
    run = st.button("Run case", type="primary", use_container_width=True)

if run:
    if not order_id:
        st.stop()
    try:
        result = run_case(order_path, order_id, pause_before="risk_scoring")
        st.session_state["result"] = result
    except Exception as exc:
        st.error(f"Execution failed: {exc}")

result = st.session_state.get("result")
if not result:
    st.info("Choose a synthetic order and run the graph to inspect its execution.")
    st.stop()

st.subheader("Decision summary")
summary = st.columns(4)
summary[0].metric("Risk score", result.get("risk_score", "n/a"))
summary[1].metric("Risk tier", result.get("risk_tier", "n/a"))
summary[2].metric("Recommendation", result.get("decision", "n/a"))
summary[3].metric("Case", result.get("case_id", "n/a"))

left, right = st.columns(2)
with left:
    st.subheader("Fraud analysis")
    st.json({
        "signals": result.get("signals", []),
        "retrieved_rules": result.get("retrieved_rules", []),
        "rag_decision": result.get("rag_decision", {}),
    })
    st.subheader("Resolution and escalation")
    st.json({
        "resolution": result.get("resolution", {}),
        "escalation": result.get("escalation", {}),
    })
with right:
    st.subheader("Memory")
    st.json({
        "working_memory": result.get("working_memory", []),
        "long_term_memory": result.get("long_term_memory", []),
    })
    st.subheader("MCP transcript")
    st.json(result.get("mcp_transcript", []))

st.subheader("Graph execution")
st.write(" -> ".join(result.get("route_history", [])))
st.json({"reflection": result.get("reflection", {}), "context_summary": result.get("context_summary", "")})

st.subheader("Project Verification / Acceptance Checklist")
verification = _verification(result)
st.dataframe(
    [{"Criterion": criterion, "Status": _status(passed)} for criterion, passed in verification.items()],
    use_container_width=True,
    hide_index=True,
)

with st.expander("Raw execution result"):
    st.code(json.dumps(result, indent=2, default=str), language="json")