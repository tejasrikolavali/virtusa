from __future__ import annotations

import json
from pathlib import Path


class ChargebackRAG:
    def __init__(self, corpus_dir: str | Path):
        self.corpus_dir = Path(corpus_dir)
        self._rules = self._load_rules()

    def _load_rules(self):
        rules = []
        for file in sorted(self.corpus_dir.glob("*.jsonl")):
            for line in file.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    parsed = json.loads(line)
                    rules.append(parsed)
                except json.JSONDecodeError:
                    continue
        return rules

    def retrieve(self, query: str, k: int = 4):
        query_lower = (query or "").lower()
        scored = []
        for rule in self._rules:
            text = f"{rule.get('type', '')} {rule.get('text', '')} {rule.get('source', '')}".lower()
            score = 0
            for token in query_lower.split():
                if token in text:
                    score += 2
            if any(word in text for word in ["fraud", "escalation", "provisional", "duplicate", "merchant", "refund"]):
                score += 1
            if score > 0:
                scored.append((score, rule))
        scored.sort(key=lambda item: item[0], reverse=True)
        results = []
        for _, rule in scored[:k]:
            results.append({
                "rule_id": rule.get("rule_id"),
                "type": rule.get("type"),
                "text": rule.get("text"),
                "source": rule.get("source"),
                "score": round((max(1, len(query_lower.split())) / max(len(rule.get("text", "").split()), 1)) * 2, 2),
            })
        return results
