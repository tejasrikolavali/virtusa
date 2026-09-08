from .manager import TieredMemory

def recall_long_term(memory: TieredMemory, case_id: str, query: str = ""):
    return memory.recall(case_id, query)
