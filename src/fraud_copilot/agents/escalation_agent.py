from ..schemas import EscalationOutput

def create_escalation(risk_tier: str, reasons: list[str]) -> EscalationOutput:
    required = risk_tier == "HIGH"
    return EscalationOutput(
        required=required,
        priority="HIGH" if required else "LOW",
        reason="; ".join(reasons) if reasons else "No escalation reason.",
    )
