from __future__ import annotations

from time import perf_counter

import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> tuple[np.ndarray, float]:
        start = perf_counter()
        vectors = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(vectors, dtype="float32"), (perf_counter() - start) * 1000

