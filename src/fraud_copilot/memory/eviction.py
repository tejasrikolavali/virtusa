from .manager import TieredMemory

def apply_eviction_policy(memory: TieredMemory, max_items: int = 50):
    memory.evict(max_items=max_items)
