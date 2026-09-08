def supervisor_route(state: dict) -> str:
    """State-driven supervisor route."""
    if not state.get("signals"):
        return "signal"
    if "risk_score" not in state:
        return "risk"
    if not state.get("resolution"):
        return "resolution"
    if state.get("risk_tier") == "HIGH" and not state.get("escalation"):
        return "escalation"
    return "done"

def reflection_route(state: dict) -> str:
    reflection = state.get("reflection", {})
    if reflection.get("action") == "RETRY" and state.get("retry_count", 0) < 2:
        return "retry"
    return "finalize"
