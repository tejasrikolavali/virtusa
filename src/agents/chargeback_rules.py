from __future__ import annotations

from pathlib import Path

from src.tools.rag_tool import ChargebackRAG


def retrieve_rules(state):
    dispute = state.get("dispute", {})
    dispute_type = state.get("dispute_type", "other_supported_dispute")
    query = f"{dispute_type} {dispute.get('merchant', '')} {dispute.get('transaction_status', '')} {dispute.get('amount', '')}"
    rag = ChargebackRAG(Path(__file__).resolve().parents[2] / "data" / "policy_corpus")
    rules = rag.retrieve(query, k=3)
    state["retrieved_rules"] = rules
    state["rule_query"] = query
    state["status"] = "rules_fetched"
    state["route_history"] = state.get("route_history", []) + ["chargeback_rules"]
    return state
