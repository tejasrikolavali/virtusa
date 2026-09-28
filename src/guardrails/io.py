import re
from typing import Any

PATTERNS = [
    r"ignore previous instructions",
    r"reveal another customer",
    r"show me the full card number",
    r"override rules",
    r"bypass fraud",
]


def validate_input(payload):
    if not isinstance(payload, dict):
        raise ValueError("Input must be a JSON object.")
    required = {"dispute_id", "transaction_id", "customer_id", "amount", "merchant", "transaction_status", "dispute_text"}
    missing = sorted(required - set(payload.keys()))
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    text = str(payload.get("dispute_text", "")).lower()
    for pattern in PATTERNS:
        if re.search(pattern, text):
            raise ValueError("Untrusted instruction-like customer content blocked.")
    return True


def sanitize_output(value: Any) -> Any:
    if isinstance(value, str):
        value = re.sub(r"\b\d{13,19}\b", "[REDACTED_PAN]", value)
        value = re.sub(r"\b\d{8,12}\b", "[REDACTED_ACCOUNT]", value)
        return value
    if isinstance(value, dict):
        return {k: sanitize_output(v) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize_output(v) for v in value]
    return value
