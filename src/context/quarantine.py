def quarantine_customer_text(text: str) -> dict:
    return {"trusted": False, "handling": "DATA_ONLY_NO_INSTRUCTIONS", "text": text}
