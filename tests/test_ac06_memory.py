from src.fraud_copilot.memory.manager import TieredMemory
from pathlib import Path

def test_ac06_memory(tmp_path):
    m = TieredMemory(tmp_path/"m.sqlite", tmp_path/"semantic")
    m.remember("CASE-1", "customer previously disputed synthetic order", importance=8)
    assert m.recall("CASE-1", "disputed")
