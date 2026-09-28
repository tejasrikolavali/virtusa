from __future__ import annotations

from src.context.pipeline import isolate_untrusted_text


def classify_dispute(state):
    dispute = state.get("dispute", {})
    raw_text = str(dispute.get("dispute_text", "")).lower()
    state["quarantined_text"] = isolate_untrusted_text(dispute)

    if any(token in raw_text for token in ["unauthorized", "not me", "not mine", "fraudulent", "someone else"]):
        dispute_type = "unauthorized_transaction"
    elif any(token in raw_text for token in ["duplicate", "charged twice", "same transaction", "second charge"]):
        dispute_type = "duplicate_transaction"
    elif any(token in raw_text for token in ["not received", "did not receive", "missing", "never arrived"]):
        dispute_type = "transaction_not_received"
    elif any(token in raw_text for token in ["amount", "charged", "incorrect", "overcharged", "wrong amount"]):
        dispute_type = "incorrect_amount"
    elif any(token in raw_text for token in ["merchant", "refund", "store", "service"]):
        dispute_type = "merchant_dispute"
    else:
        dispute_type = "other_supported_dispute"

    if float(dispute.get("amount", 0) or 0) >= 2500:
        dispute_type = "high_value_dispute" if dispute_type == "other_supported_dispute" else dispute_type

    state["dispute_type"] = dispute_type
    state["status"] = "classified"
    state["route_history"] = state.get("route_history", []) + ["dispute_classifier"]
    return state
