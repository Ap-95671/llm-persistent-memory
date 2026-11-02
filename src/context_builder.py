from __future__ import annotations

from time import perf_counter


class TokenCounter:
    def __init__(self, model_name: str):
        from transformers import AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def count(self, text: str) -> int:
        return len(self.tokenizer.encode(text, add_special_tokens=False))


def _format_memories(memories: list[dict]) -> str:
    return "\n".join(f"- [{m['timestamp']}] ({m['id']}) {m['text']}" for m in memories) or "- None"


def build_context(condition: str, case: dict, retrieved: list[dict], counter: TokenCounter, recent_limit: int, full_budget: int) -> tuple[str, dict]:
    start = perf_counter()
    history = case["history"]
    recent = history[-recent_limit:] if recent_limit else []
    recent_text = "\n".join(f"{m['role'].title()}: {m['text']}" for m in recent)
    full_used, truncated = [], False
    if condition == "recent_context":
        historical_block, memory_block = "", ""
    elif condition == "full_history":
        # Deterministic policy: retain the newest complete messages fitting the budget.
        running = 0
        for mem in reversed(history):
            line = f"{mem['role'].title()}: [{mem['timestamp']}] {mem['text']}"
            size = counter.count(line)
            if running + size > full_budget:
                truncated = True; continue
            full_used.append(mem); running += size
        full_used.reverse()
        historical_block = "Full conversation history:\n" + "\n".join(f"{m['role'].title()}: [{m['timestamp']}] {m['text']}" for m in full_used)
        memory_block = ""
        recent_text = ""  # Avoid duplication: full history already contains recent turns.
    else:
        historical_block = ""
        memory_block = "Relevant information from previous interactions:\n" + _format_memories(retrieved)
    parts = [x for x in [memory_block, historical_block, "Recent conversation:\n"+recent_text if recent_text else "", "Current user query:\n"+case["evaluation_query"]] if x]
    prompt = "\n\n".join(parts)
    recent_tokens = counter.count(recent_text)
    historical_tokens = counter.count(historical_block)
    memory_tokens = counter.count(memory_block)
    metrics = {"recent_context_tokens":recent_tokens, "historical_context_tokens":historical_tokens, "memory_tokens":memory_tokens, "prompt_tokens":counter.count(prompt), "context_construction_latency_ms":(perf_counter()-start)*1000, "full_history_truncated":truncated, "full_history_memory_ids":[m["id"] for m in full_used]}
    return prompt, metrics

