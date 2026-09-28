from __future__ import annotations

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("transaction-dispute-fraud-triage")

ROOT = Path(__file__).resolve().parent.parent
RULES_PATH = ROOT / "data" / "policy_corpus" / "rules.jsonl"

TRANSACTIONS = {
    "TXN-001": {"transaction_id": "TXN-001", "customer_id": "CUSTOMER-001", "amount": 1250.0, "currency": "USD", "merchant": "Synthetic Electronics", "status": "posted", "card_last4": "4242"},
    "TXN-002": {"transaction_id": "TXN-002", "customer_id": "CUSTOMER-002", "amount": 500.0, "currency": "USD", "merchant": "Cloud Travel", "status": "posted", "card_last4": "1002"},
    "TXN-003": {"transaction_id": "TXN-003", "customer_id": "CUSTOMER-003", "amount": 2450.0, "currency": "USD", "merchant": "Northwind Market", "status": "pending", "card_last4": "3705"},
}

PRIOR_DISPUTES = {
    "CUSTOMER-001": [{"customer_id": "CUSTOMER-001", "dispute_id": "DISP-021", "transaction_id": "TXN-099", "amount": 799.0, "status": "closed"}],
    "CUSTOMER-002": [{"customer_id": "CUSTOMER-002", "dispute_id": "DISP-098", "transaction_id": "TXN-110", "amount": 95.0, "status": "denied"}],
    "CUSTOMER-003": [{"customer_id": "CUSTOMER-003", "dispute_id": "DISP-015", "transaction_id": "TXN-042", "amount": 180.0, "status": "resolved"}],
}


@mcp.tool()
def transaction_lookup(transaction_id: str) -> dict:
    return TRANSACTIONS.get(transaction_id, {"error": "NOT_FOUND"})


@mcp.tool()
def prior_disputes(customer_id: str) -> list[dict]:
    return PRIOR_DISPUTES.get(customer_id, [])


@mcp.resource("policy://chargeback-rules")
def chargeback_rules_resource() -> str:
    if not RULES_PATH.exists():
        return json.dumps({"status": "no_rules", "message": "Synthetic policy corpus is empty."})
    rows = [json.loads(line) for line in RULES_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    return json.dumps(rows, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
