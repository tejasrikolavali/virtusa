from __future__ import annotations


def write_context(state):
    dispute = state.get("dispute", {})
    fact = {
        "dispute_id": dispute.get("dispute_id"),
        "transaction_id": dispute.get("transaction_id"),
        "amount": dispute.get("amount"),
        "merchant": dispute.get("merchant"),
        "dispute_type": state.get("dispute_type"),
    }
    state["working_memory"] = state.get("working_memory", []) + [fact]
    state["long_term_memory"] = state.get("long_term_memory", []) + [fact]
    return state


def select_context(state):
    dispute = state.get("dispute", {})
    selected = {
        "dispute_id": dispute.get("dispute_id"),
        "transaction_id": dispute.get("transaction_id"),
        "amount": dispute.get("amount"),
        "merchant": dispute.get("merchant"),
        "dispute_type": state.get("dispute_type"),
        "risk_tier": state.get("risk_tier"),
        "retrieved_rules": state.get("retrieved_rules", [])[:3],
    }
    state["context_summary"] = str(selected)
    return state


def compress_context(state):
    messages = state.get("messages", [])
    if len(messages) > 4:
        compressed = {"role": "system", "content": "Compressed historical context: prior dispute reviewed; risk and policy evidence retained."}
        state["messages"] = [compressed] + messages[-3:]
    return state


def isolate_untrusted_text(dispute):
    text = str(dispute.get("dispute_text", ""))
    return {
        "trusted": False,
        "handling": "DATA_ONLY_NO_INSTRUCTIONS",
        "text": text,
        "contains_instruction_like_content": any(
            marker in text.lower() for marker in ["ignore previous instructions", "reveal another customer", "show me the full card number"]
        ),
    }
