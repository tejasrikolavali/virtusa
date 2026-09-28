# Output-risk classification

This project uses a conservative risk gate for generated outputs.

## Tier definitions
- Low risk: routine informational or policy retrieval outputs that do not change customer outcomes or create a financial decision. These are recorded in the workflow but do not trigger a hold.
- Medium risk: dispute classification, fraud score summaries, or policy-match explanations that influence an internal review decision. These remain subject to the existing human escalation rules in [src/agents/resolution.py](src/agents/resolution.py).
- High risk: output that recommends a final customer action, large monetary exposure, or escalates a high-value/high-score dispute. Those cases are routed to human review before any final action is committed in the policy layer.

## Review gate
- The high-risk decision gate is implemented in [src/agents/resolution.py](src/agents/resolution.py) by checking `fraud_score >= 75` or amount thresholds before allowing an automated final action.
- Guardrails for input validation and output sanitization live in [src/guardrails/io.py](src/guardrails/io.py).
- Context isolation and quarantining are enforced in [src/context/pipeline.py](src/context/pipeline.py).

## Refusal behavior
- Untrusted or instruction-like customer text triggers validation errors rather than being treated as instructions.
- Card/account-like strings are redacted before output is returned or logged.
