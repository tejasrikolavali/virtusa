import sqlite3
from pathlib import Path


class TieredMemory:
    def __init__(self, db_path: str | Path, max_items: int = 50):
        self.db_path = Path(db_path)
        self.max_items = max_items
        self.working = {}
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS memories("
                "id INTEGER PRIMARY KEY, case_id TEXT, fact TEXT, importance INTEGER, "
                "created REAL DEFAULT(strftime('%s','now')) )"
            )

    def remember(self, case_id, fact, importance=5):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO memories(case_id, fact, importance) VALUES (?, ?, ?)",
                (str(case_id), str(fact), int(importance)),
            )
            rows = conn.execute(
                "SELECT id, case_id, fact, importance FROM memories WHERE case_id = ? ORDER BY importance DESC, created DESC",
                (str(case_id),),
            ).fetchall()
            if len(rows) > self.max_items:
                excess = rows[self.max_items:]
                for item in excess:
                    conn.execute("DELETE FROM memories WHERE id = ?", (item[0],))

    def recall(self, case_id):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT fact FROM memories WHERE case_id = ? ORDER BY importance DESC, created DESC",
                (str(case_id),),
            ).fetchall()
        return [row[0] for row in rows]

    def recall_all(self):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT case_id, fact, importance FROM memories ORDER BY importance DESC, created DESC"
            ).fetchall()
        return [{"case_id": row[0], "fact": row[1], "importance": row[2]} for row in rows]
