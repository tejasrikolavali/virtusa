# Business Case

## Problem
An online retailer wants to catch fraudulent orders without unnecessarily harming good customers. The copilot gathers risk signals, scores an order, drafts a hold/release/review decision and escalates where needed.

## Actors
- Fraud triage copilot
- Fraud/risk analyst
- Synthetic order/customer data source
- MCP tooling
- Fraud-policy knowledge base

## Success metrics
- Correct state-driven routing
- Traceable risk rationale
- Grounded fraud-policy lookup
- Cross-session case continuity
- Safe handling of untrusted text
- Reproducible local execution

## Scope
Only synthetic data and simulated actions are used. No real order-management or payment-gateway action is executed.
