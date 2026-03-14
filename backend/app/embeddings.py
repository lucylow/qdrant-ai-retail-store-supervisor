from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, List, Sequence

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import MODELS


@dataclass(frozen=True)
class EmbeddingResult:
    vectors: np.ndarray
    model_name: str


@lru_cache(maxsize=2)
def _load_text_model() -> SentenceTransformer:
    # CURSOR: swap to quantized / local model if needed.
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
    """Return vector size of the text embedding model (e.g. 768 for all-mpnet-base-v2)."""
    model = _load_text_model()
    return model.get_sentence_embedding_dimension()


def normalize_rows(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    return matrix / norms


def as_list(vectors: np.ndarray) -> list[list[float]]:
    return vectors.tolist()


__all__ = ["EmbeddingResult", "embed_texts", "embed_single", "get_text_embedding_dimension", "normalize_rows", "as_list"]

from typing import Iterable, List
import numpy as np
import logging
from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL, IMAGE_EMBEDDING_MODEL, EMBED_BATCH

logger = logging.getLogger(__name__)
_text_model = SentenceTransformer(EMBEDDING_MODEL)


def embed_texts(texts: Iterable[str]) -> np.ndarray:
    texts = list(texts)
    if not texts:
        return np.empty((0, _text_model.get_sentence_embedding_dimension()), dtype="float32")
    arr = _text_model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return arr.astype("float32")


def embed_text_batch_generator(iterable: Iterable[str], batch_size: int = EMBED_BATCH):
    batch: List[str] = []
    for t in iterable:
        batch.append(t)
        if len(batch) >= batch_size:
            yield embed_texts(batch)
            batch = []
    if batch:
        yield embed_texts(batch)


def embed_image(path: str):
    # Best-effort CLIP via SentenceTransformers; fallback to zeros
    try:
        m = SentenceTransformer(IMAGE_EMBEDDING_MODEL)
        vec = m.encode([path], convert_to_numpy=True)[0]
        return vec.astype("float32")
    except Exception as e:  # noqa: BLE001
        logger.warning("image embed fallback: %s", e)
        return np.zeros(512, dtype="float32")

from typing import Iterable, List
import numpy as np
import logging
from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL, EMBED_BATCH, IMAGE_EMBEDDING_MODEL

logger = logging.getLogger(__name__)

_text_model: SentenceTransformer = SentenceTransformer(EMBEDDING_MODEL)


def embed_texts(texts: Iterable[str]) -> np.ndarray:
    """
    Returns a numpy array of shape (n, dim). Always float32.
    """
    texts = list(texts)
    if not texts:
        return np.empty((0, _text_model.get_sentence_embedding_dimension()), dtype="float32")
    vecs = _text_model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return vecs.astype("float32")


def embed_text_batch_generator(iterable, batch_size: int = EMBED_BATCH):
    """
    Generator yields batches of vectors for a streaming ingestion pipeline.
    """
    batch: List[str] = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= batch_size:
            yield embed_texts(batch)
            batch = []
    if batch:
        yield embed_texts(batch)


def embed_image(path: str):
    try:
        model = SentenceTransformer(IMAGE_EMBEDDING_MODEL)
        emb = model.encode([path], convert_to_numpy=True)
        return emb[0].astype("float32")
    except Exception as e:  # noqa: BLE001
        logger.warning("Image embedding failed, using fallback: %s", e)
        # fallback: return zeros of a reasonable size
        return np.zeros(512, dtype="float32")

