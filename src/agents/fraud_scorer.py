from __future__ import annotations


def score_fraud(state):
    dispute = state.get("dispute", {})
    amount = float(dispute.get("amount", 0) or 0)
    prior = int(dispute.get("prior_disputes", 0) or 0)
    status = str(dispute.get("transaction_status", "")).lower()
    country = str(dispute.get("country", "US")).upper()
    merchant = str(dispute.get("merchant", "")).lower()
    text = str(dispute.get("dispute_text", "")).lower()

    score = 10
    factors = []

    if amount >= 2000:
        score += 25
        factors.append("High transaction amount above policy threshold.")
    if prior >= 2:
        score += 20
        factors.append("Multiple prior disputes increase risk.")
    if "unauthorized" in text or "not me" in text:
        score += 25
        factors.append("Dispute text indicates possible unauthorized use.")
    if status not in {"posted", "settled"}:
        score += 15
        factors.append("Payment status is abnormal for a settled card transaction.")
    if country not in {"US", "CA", "GB", "AU"}:
        score += 10
        factors.append("Country mismatch or unusual geography pattern.")
    if "gift" in merchant or "travel" in merchant or "crypto" in merchant:
        score += 10
        factors.append("Merchant category is associated with elevated fraud exposure.")

    score = min(score, 100)
    if score >= 75:
        risk_tier = "high"
    elif score >= 40:
        risk_tier = "medium"
    else:
        risk_tier = "low"

    state["fraud_score"] = round(score, 2)
    state["risk_tier"] = risk_tier
    state["fraud_factors"] = factors[:5]
    state["status"] = "scored"
    state["route_history"] = state.get("route_history", []) + ["fraud_scorer"]
    return state
