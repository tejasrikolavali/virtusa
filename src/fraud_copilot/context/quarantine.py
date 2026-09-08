def quarantine_order_text(order: dict) -> dict:
    """NFR-03: free-text is data, never an instruction."""
    return {
        "customer_free_text": order.get("customer_free_text", ""),
        "order_free_text": order.get("order_free_text", ""),
        "trusted": False,
        "handling": "DATA_ONLY_NO_INSTRUCTIONS",
    }
