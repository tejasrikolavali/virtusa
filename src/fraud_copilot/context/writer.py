def write_context(state: dict) -> dict:
    order = state.get("order", {})
    return {
        "case_id": state.get("case_id"),
        "order_id": order.get("order_id"),
        "amount": order.get("amount"),
        "payment_status": order.get("payment_status"),
        "country": order.get("country"),
        "signals": state.get("signals", []),
    }
