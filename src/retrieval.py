from __future__ import annotations

from datetime import datetime
from time import perf_counter

import numpy as np

from src.memory_store import MemoryStore


def semantic_retrieve(store: MemoryStore, query_vector: np.ndarray, k: int, threshold: float | None = None) -> tuple[list[dict], float]:
    start = perf_counter()
    hits = store.semantic_search(query_vector, k)
    out = []
    for idx, score in hits:
        if threshold is None or score >= threshold:
            out.append(store.memories[idx] | {"semantic_score": score, "retrieval_score": score})
    return out, (perf_counter() - start) * 1000


def temporal_retrieve(store: MemoryStore, query_vector: np.ndarray, k: int, alpha: float, beta: float, temporal_lambda: float, query_time: datetime, threshold: float | None = None) -> tuple[list[dict], float]:
    start = perf_counter()
    semantic = store.vectors @ query_vector
    # Cosine similarities are mapped from [-1,1] to [0,1] before combination.
    semantic_norm = (semantic + 1.0) / 2.0
    ages = np.array([max(0.0, (query_time - datetime.fromisoformat(m["timestamp"])).total_seconds() / 86400) for m in store.memories])
    temporal = np.exp(-temporal_lambda * ages)
    composite = alpha * semantic_norm + beta * temporal
    order = np.argsort(-composite)[: min(k, len(store.memories))]
    out = []
    for idx in order:
        if threshold is None or composite[idx] >= threshold:
            out.append(store.memories[int(idx)] | {"semantic_score": float(semantic[idx]), "temporal_score": float(temporal[idx]), "retrieval_score": float(composite[idx])})
    return out, (perf_counter() - start) * 1000

