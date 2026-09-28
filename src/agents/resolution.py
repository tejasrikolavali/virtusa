from __future__ import annotations


def resolve(state):
    dispute = state.get("dispute", {})
    fraud_score = float(state.get("fraud_score", 0) or 0)
    dispute_type = state.get("dispute_type", "other_supported_dispute")
    rules = state.get("retrieved_rules", []) or []
    rule_ids = [item.get("rule_id", "unknown") for item in rules]

    if fraud_score >= 75 or dispute.get("amount", 0) >= 5000:
        action = "investigate"
        rationale = "High risk and/or high-value dispute requires human review and additional evidence."
        escalation = True
    elif dispute_type in {"unauthorized_transaction", "transaction_not_received"} and fraud_score < 60:
        action = "provisional_credit"
        rationale = "Customer claim is supported by the dispute type and the fraud profile remains below escalation threshold."
        escalation = False
    elif dispute_type == "duplicate_transaction":
        action = "deny"
        rationale = "Duplicate or repeated charges are most consistent with a non-fraudulent duplicate payment scenario."
        escalation = False
    elif dispute_type == "incorrect_amount":
        action = "investigate"
        rationale = "Amount mismatch needs validation against billing and merchant settlement evidence."
        escalation = False
    else:
        action = "investigate"
        rationale = "Policy evidence and fraud signals require review before a final disposition."
        escalation = False

    state["decision"] = {
        "recommended_action": action,
        "rationale": rationale,
        "human_escalation": escalation,
        "cited_rules": rule_ids,
        "risk_tier": state.get("risk_tier", "medium"),
    }
    state["human_escalation"] = escalation
    state["status"] = "resolved"
    state["route_history"] = state.get("route_history", []) + ["resolution"]
    return state
