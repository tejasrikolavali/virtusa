import json
import sqlite3
import time
from pathlib import Path

class TieredMemory:
    """Short-term working memory plus persistent deterministic long-term memory.

    The public interface is intentionally simple so cross-session behavior and
    importance-based eviction remain reproducible without an external service.
    """
    def __init__(self, db_path: Path, collection_dir: Path):
        self.db_path = Path(db_path)
        self.collection_dir = Path(collection_dir)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.collection_dir.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as con:
            con.execute("""CREATE TABLE IF NOT EXISTS memories(
                id TEXT PRIMARY KEY, case_id TEXT, fact TEXT, importance INTEGER,
                created REAL, last_used REAL, ttl REAL
            )""")
        self.working = {}

    def remember(self, case_id, fact, importance=5, ttl=None, memory_id=None):
        memory_id = memory_id or f"{case_id}-{int(time.time()*1000000)}"
        now = time.time()
        with sqlite3.connect(self.db_path) as con:
            con.execute(
                "INSERT OR REPLACE INTO memories VALUES(?,?,?,?,?,?,?)",
                (memory_id, case_id, fact, int(importance), now, now,
                 None if ttl is None else now + ttl),
            )
        self.working.setdefault(case_id, []).append({"id": memory_id, "fact": fact})
        return memory_id

    def recall(self, case_id, query=""):
        now = time.time()
        with sqlite3.connect(self.db_path) as con:
            rows = con.execute(
                "SELECT id,fact,importance,created,last_used,ttl FROM memories WHERE case_id=?",
                (case_id,),
            ).fetchall()
            results = []
            for r in rows:
                if r[5] is not None and r[5] < now:
                    continue
                if not query or query.lower() in r[1].lower():
                    results.append({
                        "id": r[0], "fact": r[1], "importance": r[2],
                        "created": r[3], "last_used": r[4], "ttl": r[5]
                    })
                    con.execute("UPDATE memories SET last_used=? WHERE id=?", (now, r[0]))
        return results

    def evict(self, max_items=50):
        now = time.time()
        with sqlite3.connect(self.db_path) as con:
            con.execute("DELETE FROM memories WHERE ttl IS NOT NULL AND ttl < ?", (now,))
            count = con.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            if count > max_items:
                excess = count - max_items
                con.execute("""
                    DELETE FROM memories WHERE id IN (
                        SELECT id FROM memories
                        ORDER BY importance ASC, last_used ASC
                        LIMIT ?
                    )
                """, (excess,))

    def clear(self):
        with sqlite3.connect(self.db_path) as con:
            con.execute("DELETE FROM memories")
        self.working.clear()
