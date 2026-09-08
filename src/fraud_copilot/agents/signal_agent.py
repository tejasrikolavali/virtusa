from ..schemas import SignalOutput

def collect_signals(order: dict) -> SignalOutput:
    signals = []
    if order.get("billing_shipping_match") is False:
        signals.append({"name": "billing_shipping_mismatch", "weight": 25})
    if order.get("payment_status") != "verified":
        signals.append({"name": "payment_not_verified", "weight": 30})
    if order.get("velocity_24h", 0) >= 5:
        signals.append({"name": "high_velocity", "weight": 20})
    if order.get("device_new") is True:
        signals.append({"name": "new_device", "weight": 10})
    if order.get("amount", 0) >= 1000:
        signals.append({"name": "high_value_order", "weight": 15})
    return SignalOutput(signals=signals)
