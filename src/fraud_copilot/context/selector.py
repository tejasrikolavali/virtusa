def select_context(state: dict, purpose: str) -> dict:
    order = state.get("order", {})
    selected = {
        "case_id": state.get("case_id"),
        "order_id": order.get("order_id"),
        "amount": order.get("amount"),
        "payment_status": order.get("payment_status"),
        "billing_shipping_match": order.get("billing_shipping_match"),
        "velocity_24h": order.get("velocity_24h"),
        "device_new": order.get("device_new"),
    }
    if purpose in {"risk", "resolution"}:
        selected["signals"] = state.get("signals", [])
        selected["retrieved_rules"] = state.get("retrieved_rules", [])
    return selected
