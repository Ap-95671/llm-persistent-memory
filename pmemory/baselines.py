"""Baselines do not execute inference on import or construction."""
class NoMemory:
    def __init__(self, recent_turns=2):
        if recent_turns < 0: raise ValueError("recent_turns must be nonnegative")
        self.recent_turns=recent_turns
    def history(self, history):
        return list(history[-self.recent_turns:]) if self.recent_turns else []

class Mem0Baseline:
    """Upstream Memory is injected; preserve default infer=True fact extraction."""
    def __init__(self, memory): self.memory=memory
    def ingest(self, messages, user_id):
        return self.memory.add(messages, user_id=user_id, infer=True)
    def retrieve(self, query, user_id, limit=5):
        return self.memory.search(query, user_id=user_id, limit=limit)
