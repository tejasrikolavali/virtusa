# Model/System card

## Model
- Planned/declared model family: Gemini via the configured `.env.example` setting `GEMINI_MODEL=gemini-2.5-flash` in [.env.example](.env.example).
- This repository is designed to use Gemini as an LLM-as-judge when a valid API key is configured in the environment; it does not commit any secret material.

## Intended use
- The system is a synthetic transaction-dispute and fraud triage copilot for dispute intake, money movement risk review, policy retrieval, and human escalation routing.
- It is intended for repo-based evaluation, synthetic policy testing, and case-study demonstration rather than real production payment operations.

## Data and scope
- All datasets are synthetic and are kept inside the repository under [data/](data/) for sample cases and policy rules.
- Customer dispute text is quarantined and treated as data-only in [src/context/pipeline.py](src/context/pipeline.py) and [src/guardrails/io.py](src/guardrails/io.py).

## Known limitations
- The rule-based dispute classification and fraud scoring in [src/agents/dispute_classifier.py](src/agents/dispute_classifier.py) and [src/agents/fraud_scorer.py](src/agents/fraud_scorer.py) are deterministic heuristics, not a live financial control engine.
- The case-study purpose is to demonstrate traceability, governance, and evidence quality, not to replace human review or a bank’s production decisioning stack.
- Actual DeepEval LLM-as-judge metrics are only populated when a valid Gemini API key is configured; otherwise the report intentionally leaves the metric values unset.

## Human oversight
- High-risk or high-value disputes require a human review gate through the escalation logic in [src/agents/resolution.py](src/agents/resolution.py).
- The end-to-end workflow is routed through [src/graph.py](src/graph.py), which also persists observability evidence for audit review.

## Out-of-scope use
- The application must not be used for live customer onboarding, legal determinations, or any real-world credit-damage decisions outside the synthetic case-study environment.
