from ..schemas import ResolutionOutput

def draft_resolution(risk_tier: str, reasons: list[str]) -> ResolutionOutput:
    if risk_tier == "HIGH":
        return ResolutionOutput(
            decision="HOLD",
            rationale="High-risk synthetic order requires manual fraud review.",
            customer_safe_note="The order is temporarily under review; no transaction action is executed by this copilot.",
        )
    if risk_tier == "MEDIUM":
        return ResolutionOutput(
            decision="REVIEW",
            rationale="Medium-risk synthetic order requires additional review.",
            customer_safe_note="The order is routed for review without executing a payment action.",
        )
    return ResolutionOutput(
        decision="RELEASE",
        rationale="Low-risk synthetic order has no sufficient hold signal.",
        customer_safe_note="The order can proceed subject to normal business controls.",
    )
