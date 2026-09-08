from src.fraud_copilot.memory.manager import TieredMemory

def test_ac07_cross_session(tmp_path):
    db = tmp_path/"memory.sqlite"
    semantic = tmp_path/"semantic"
    session1 = TieredMemory(db, semantic)
    session1.remember("CASE-CROSS", "synthetic customer prefers manual review", importance=9)

    # New memory object = new session/process boundary simulation.
    session2 = TieredMemory(db, semantic)
    recalled = session2.recall("CASE-CROSS", "manual review")
    assert recalled
    Path = __import__("pathlib").Path
    evidence = Path("evidence/AC-07")
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence/"cross_session_output.txt").write_text(
        "AC-07 PASS\\nNew memory instance recalled: " + recalled[0]["fact"] + "\\n",
        encoding="utf-8"
    )
