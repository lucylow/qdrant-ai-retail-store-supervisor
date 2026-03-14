"""
Mean/max pooling and truncation strategies for embedding pipelines.
"""
from __future__ import annotations

from typing import List, Literal, Optional

import numpy as np


def mean_pool(vectors: np.ndarray, attention_mask: Optional[np.ndarray] = None) -> np.ndarray:
    """Mean pooling over last dimension; optional mask (1 = valid)."""
    if attention_mask is not None:
        mask = attention_mask.astype(np.float32)
        mask = np.expand_dims(mask, -1)
        sum_vec = (vectors * mask).sum(axis=1)
        counts = np.maximum(mask.sum(axis=1), 1e-9)
        return (sum_vec / counts).astype(np.float32)
    return vectors.mean(axis=1).astype(np.float32)


def max_pool(vectors: np.ndarray, attention_mask: Optional[np.ndarray] = None) -> np.ndarray:
    """Max pooling over last dimension; masked positions set to large negative."""
    if attention_mask is not None:
        mask = np.expand_dims(attention_mask, -1)
        vectors = np.where(mask > 0, vectors, -1e9)
    return vectors.max(axis=1).astype(np.float32)


def truncate_sequences(
    texts: List[str],
    max_length: int,
    strategy: Literal["left", "right", "middle"] = "right",
) -> List[str]:
    """Truncate tokenized or character length; strategy: keep left/right/middle."""
    out = []
    for t in texts:
        if len(t) <= max_length:
            out.append(t)
            continue
        if strategy == "left":
            out.append(t[:max_length])
        elif strategy == "right":
            out.append(t[-max_length:])
        else:
            half = max_length // 2
            out.append(t[:half] + t[-half:])
    return out


def normalize_rows(matrix: np.ndarray) -> np.ndarray:
    """L2 normalize rows."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.where(norms == 0.0, 1.0, norms)
    return (matrix / norms).astype(np.float32)
