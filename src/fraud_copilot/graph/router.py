def route_after_risk(state: dict) -> str:
    if state.get("risk_tier") == "HIGH":
        return "resolution"
    if state.get("risk_tier") == "MEDIUM":
        return "resolution"
    return "resolution"

def route_after_resolution(state: dict) -> str:
    if state.get("risk_tier") == "HIGH":
        return "escalation"
    return "reflection"
