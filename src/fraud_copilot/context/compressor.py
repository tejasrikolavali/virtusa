def compress_messages(messages: list[dict], max_items: int = 8) -> tuple[list[dict], str]:
    if len(messages) <= max_items:
        return messages, ""
    kept = messages[-max_items:]
    summary = "Compressed earlier case activity: " + "; ".join(
        str(m.get("content", ""))[:160] for m in messages[:-max_items]
    )
    return kept, summary
