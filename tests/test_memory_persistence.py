from src.memory.manager import TieredMemory


def test_cross_session_memory(tmp_path):
    db = tmp_path / "memory.sqlite"
    memory = TieredMemory(db)
    memory.remember("CASE-TEST", "Synthetic prior review exists.", 9)
    assert "Synthetic prior review exists." in TieredMemory(db).recall("CASE-TEST")


def test_memory_retrieval_preserves_multiple_facts(tmp_path):
    db = tmp_path / "memory.sqlite"
    memory = TieredMemory(db)
    memory.remember("CASE-TEST", "Fraud review opened.", 5)
    memory.remember("CASE-TEST", "Policy evidence reviewed.", 9)
    facts = TieredMemory(db).recall("CASE-TEST")
    assert "Policy evidence reviewed." in facts
    assert len(facts) >= 2
