from pathlib import Path
from ..config import settings

def ingest():
    root = settings.data_dir / "knowledge"
    docs = list(root.rglob("*.txt"))
    return {"documents": len(docs), "index": str(settings.index_dir)}
