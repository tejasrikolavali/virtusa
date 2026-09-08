def rag_check(result: dict) -> bool:
    decision = result.get("rag_decision", {})
    if decision.get("agent_decided_to_call"):
        return bool(result.get("retrieved_rules"))
    return result.get("risk_tier") == "LOW" and not result.get("retrieved_rules")
