from .manager import TieredMemory

def get_working_memory(memory: TieredMemory, case_id: str):
    return memory.working.get(case_id, [])
