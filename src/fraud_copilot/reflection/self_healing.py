def reflect(state: dict) -> dict:
    """Validate key outputs and return an explicit self-healing decision."""
    problems = []
    try:
        risk_score = float(state.get("risk_score", -1))
    except (TypeError, ValueError):
        risk_score = -1
    if not 0 <= risk_score <= 100:
        problems.append("risk_score_out_of_range")
    if state.get("risk_tier") not in {"LOW", "MEDIUM", "HIGH"}:
        problems.append("invalid_risk_tier")
    if not state.get("decision"):
        problems.append("missing_decision")

    if problems and state.get("retry_count", 0) < 2:
        return {
            "ok": False,
            "action": "RETRY",
            "problems": problems,
            "next_retry_count": state.get("retry_count", 0) + 1,
        }
    return {
        "ok": not problems,
        "action": "CONTINUE" if not problems else "STOP_WITH_EXPLICIT_FAILURE",
        "problems": problems,
        "next_retry_count": state.get("retry_count", 0),
    }
