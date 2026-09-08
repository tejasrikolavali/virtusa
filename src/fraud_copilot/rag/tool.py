from langchain_core.tools import tool
from .retriever import FraudRuleRetriever
from ..config import settings

_retriever = FraudRuleRetriever(settings.data_dir / "knowledge")

@tool
def fraud_rule_lookup(query: str) -> str:
    """Look up synthetic fraud rules and chargeback reasons."""
    results = _retriever.search(query, k=4)
    return str(results)
