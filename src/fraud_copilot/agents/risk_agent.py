from ..schemas import RiskScoreOutput

def score_risk(signals: list[dict]) -> RiskScoreOutput:
    score = min(100, sum(int(s.get("weight", 0)) for s in signals))
    tier = "HIGH" if score >= 70 else "MEDIUM" if score >= 30 else "LOW"
    reasons = [s["name"] for s in signals]
    confidence = 0.90 if signals else 0.75
    return RiskScoreOutput(
        risk_score=score, risk_tier=tier, reasons=reasons, confidence=confidence
    )
