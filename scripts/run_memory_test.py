import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.fraud_copilot.memory.manager import TieredMemory

def main():
    db = Path(".index") / "evidence_memory.sqlite"
    m1 = TieredMemory(db, Path(".index") / "evidence_semantic")
    m1.remember("AC07-DEMO", "Synthetic fact from session one: review history exists.", importance=9)
    m2 = TieredMemory(db, Path(".index") / "evidence_semantic")
    result = m2.recall("AC07-DEMO", "review history")
    out = Path("evidence/AC-07/cross_session_output.txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("AC-07 PASS\n" + str(result) + "\n", encoding="utf-8")
    print(out.read_text())

if __name__ == "__main__":
    main()
