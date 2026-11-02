from __future__ import annotations

from dataclasses import dataclass

import faiss
import numpy as np


@dataclass
class MemoryStore:
    memories: list[dict]
    vectors: np.ndarray

    def __post_init__(self) -> None:
        if len(self.memories) != len(self.vectors):
            raise ValueError("Memory/vector count mismatch")
        self.index = faiss.IndexFlatIP(self.vectors.shape[1])
        self.index.add(self.vectors)

    def semantic_search(self, query_vector: np.ndarray, k: int) -> list[tuple[int, float]]:
        scores, indices = self.index.search(query_vector.reshape(1, -1), min(k, len(self.memories)))
        return [(int(i), float(s)) for i, s in zip(indices[0], scores[0]) if i >= 0]

