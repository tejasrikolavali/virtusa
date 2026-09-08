import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.fraud_copilot.rag.retriever import FraudRuleRetriever
from src.fraud_copilot.config import settings

def main():
    r = FraudRuleRetriever(settings.data_dir / "knowledge")
    result = r.search("payment mismatch fraud chargeback", k=4)
    out = Path("evidence/AC-11/agentic_rag_trace.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "AC": "AC-11",
        "agent_decision": "CALL_RAG",
        "query": "payment mismatch fraud chargeback",
        "results": result
    }, indent=2), encoding="utf-8")
    print(out.read_text())

if __name__ == "__main__":
    main()
