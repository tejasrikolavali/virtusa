from src.fraud_copilot.memory.manager import TieredMemory

def test_ac08_eviction(tmp_path):
    m = TieredMemory(tmp_path/"m.sqlite", tmp_path/"semantic")
    m.remember("CASE-E", "low importance temporary", importance=1)
    m.remember("CASE-E", "high importance fact", importance=10)
    m.evict(max_items=1)
    rows = m.recall("CASE-E")
    assert len(rows) == 1
    assert rows[0]["importance"] == 10
