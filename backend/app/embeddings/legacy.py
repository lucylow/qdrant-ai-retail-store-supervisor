# Legacy embedding API for backward compatibility (used by app.embeddings package).
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import List, Sequence

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import MODELS


@dataclass(frozen=True)
class EmbeddingResult:
    vectors: np.ndarray
    model_name: str

    def __getitem__(self, i: int) -> np.ndarray:
        return self.vectors[i]


@lru_cache(maxsize=2)
def _load_text_model() -> SentenceTransformer:
    return SentenceTransformer(MODELS.text_embedding_model)


def embed_texts(texts: Sequence[str], batch_size: int = 32) -> EmbeddingResult:
    model = _load_text_model()
    vectors: List[List[float]] = []
    for start in range(0, len(texts), batch_size):
        batch = list(texts[start : start + batch_size])
        if not batch:
            continue
        emb = model.encode(batch, convert_to_numpy=True, show_progress_bar=False)
        vectors.append(emb)  # type: ignore[arg-type]
    if not vectors:
        return EmbeddingResult(
            vectors=np.zeros((0, model.get_sentence_embedding_dimension()), dtype=np.float32),
            model_name=MODELS.text_embedding_model,
        )
    stacked = np.vstack(vectors)
    return EmbeddingResult(vectors=stacked.astype(np.float32), model_name=MODELS.text_embedding_model)


def embed_single(text: str) -> EmbeddingResult:
    return embed_texts([text], batch_size=1)


def get_text_embedding_dimension() -> int:
    model = _load_text_model()
    return model.get_sentence_embedding_dimension()


def normalize_rows(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    return matrix / norms


def as_list(vectors: np.ndarray) -> list[list[float]]:
    return vectors.tolist()


def embed_image(path: str) -> np.ndarray:
    try:
        m = SentenceTransformer(MODELS.image_embedding_model)
        vec = m.encode([path], convert_to_numpy=True)[0]
        return vec.astype(np.float32)
    except Exception:
        return np.zeros(512, dtype=np.float32)
