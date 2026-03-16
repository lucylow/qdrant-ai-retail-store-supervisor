"""
HuggingFace Inference API: multimodal embeddings (bge-m3 text, CLIP image).

Free tier: 5M tokens/month. Models: BAAI/bge-m3 (1024d), openai/clip-vit-base-patch32 (512d).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import requests

from app.config import EXTERNAL_PROVIDERS
from app.multimodal.schema import TEXT_DIM, IMAGE_DIM

logger = logging.getLogger(__name__)

HF_API_BASE = "https://api-inference.huggingface.co/models"


def _pad_or_truncate(vec: List[float], target_dim: int) -> List[float]:
    out = [0.0] * target_dim
    n = min(len(vec), target_dim)
    for i in range(n):
        out[i] = vec[i]
    # normalize
    norm = sum(x * x for x in out) ** 0.5
    if norm > 1e-9:
        out = [x / norm for x in out]
    return out


def _embed_text_hf(text: str) -> Optional[List[float]]:
    """Embed text via HF Inference (bge-m3). Returns 1024d; caller pads to TEXT_DIM."""
    token = EXTERNAL_PROVIDERS.hf_token
    if not token:
        return None
    url = f"{HF_API_BASE}/{EXTERNAL_PROVIDERS.hf_text_model}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"inputs": text}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            # [[float,...]]
            vec = data[0] if data else []
        elif isinstance(data, dict) and "embedding" in data:
            vec = data["embedding"]
        else:
            vec = data if isinstance(data, list) else []
        if vec:
            return _pad_or_truncate(vec, TEXT_DIM)
    except Exception as e:
        logger.warning("HF text embed failed: %s", e)
    return None


def _embed_image_hf(image_bytes: bytes) -> Optional[List[float]]:
    """Embed image via HF Inference (CLIP). Returns 512d (IMAGE_DIM)."""
    token = EXTERNAL_PROVIDERS.hf_token
    if not token:
        return None
    url = f"{HF_API_BASE}/{EXTERNAL_PROVIDERS.hf_image_model}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.post(url, data=image_bytes, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            vec = data[0] if data else []
        elif isinstance(data, dict) and "embedding" in data:
            vec = data["embedding"]
        else:
            vec = data if isinstance(data, list) else []
        if vec:
            return _pad_or_truncate(vec, IMAGE_DIM)
    except Exception as e:
        logger.warning("HF image embed failed: %s", e)
    return None


def embed_multimodal_hf(
    text: str,
    image: Optional[bytes] = None,
) -> Dict[str, Any]:
    """
    Multimodal embeddings via HuggingFace Inference API.

    Returns:
        {"textvector": list[float] | None, "imagevector": list[float] | None}
    """
    result: Dict[str, Any] = {"textvector": None, "imagevector": None}
    if text:
        result["textvector"] = _embed_text_hf(text)
    if image:
        result["imagevector"] = _embed_image_hf(image)
    return result
