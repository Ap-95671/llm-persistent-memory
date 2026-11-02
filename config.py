"""Frozen experiment configuration; pilot selection writes chosen values here only in run metadata."""
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ExperimentConfig:
    random_seed: int = 20260824
    ollama_url: str = "http://127.0.0.1:11434"
    llm_model: str = "qwen2.5:3b"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    tokenizer_model: str = "Qwen/Qwen2.5-3B-Instruct"
    system_prompt: str = (
        "Answer the user's question using only information in the supplied conversation "
        "and memory. Give the requested value concisely. If it is unavailable, say "
        "'I don't know'. Prefer explicit newer updates over older statements."
    )
    temperature: float = 0.0
    top_p: float = 0.9
    max_generated_tokens: int = 48
    generation_seed: int = 20260824
    context_window: int = 8192
    recent_turn_limit: int = 2
    full_history_token_budget: int = 7000
    temporal_lambda: float = 0.08
    pilot_k_values: tuple[int, ...] = (3, 5, 10)
    pilot_alpha_values: tuple[float, ...] = (0.9, 0.8, 0.7, 0.6, 0.5)
    relevance_threshold: float | None = None

    def to_dict(self) -> dict:
        return asdict(self)


CONFIG = ExperimentConfig()

