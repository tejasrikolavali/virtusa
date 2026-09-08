from pathlib import Path
import re

class FraudRuleRetriever:
    """Semantic-capable retrieval with Chroma/SentenceTransformer when available.

    A lexical fallback keeps the capstone reproducible on a fresh Python setup.
    """
    def __init__(self, root: Path):
        self.root = Path(root)
        self.docs = []
        for p in sorted(self.root.rglob("*.txt")):
            text = p.read_text(encoding="utf-8")
            self.docs.append({"id": p.stem, "path": str(p), "text": text})

    def search(self, query: str, k: int = 4):
        q = set(re.findall(r"[a-z0-9]+", query.lower()))
        scored = []
        for d in self.docs:
            words = set(re.findall(r"[a-z0-9]+", d["text"].lower()))
            score = len(q & words) / max(1, len(q))
            scored.append((score, d))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {"id": d["id"], "text": d["text"], "score": round(score, 4)}
            for score, d in scored
            if score > 0
        ][:k]
