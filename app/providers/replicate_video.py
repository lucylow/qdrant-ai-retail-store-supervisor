"""
Replicate API: video → embeddings (e.g. VideoCLIP / video-ldm for product demos).

~$0.01/10s clip. Optional for production pipeline when top result has video_demo.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, List, Optional

from app.config import EXTERNAL_PROVIDERS
from app.multimodal.schema import VIDEO_DIM

logger = logging.getLogger(__name__)


def _pad_or_truncate(vec: List[float], target_dim: int) -> List[float]:
    out = [0.0] * target_dim
    n = min(len(vec), target_dim)
    for i in range(n):
        out[i] = vec[i]
    norm = sum(x * x for x in out) ** 0.5
    if norm > 1e-9:
        out = [x / norm for x in out]
    return out


def extract_video_vectors_replicate(
    video_path: str,
    *,
    model_ref: str = "laion-ai/video-ldm",
) -> Optional[List[float]]:
    """
    Extract embedding from video via Replicate. Returns VIDEO_DIM-sized vector or None.

    When Replicate model returns different dim, we pad/truncate to VIDEO_DIM.
    """
    if not EXTERNAL_PROVIDERS.replicate_api_token:
        logger.debug("REPLICATE_API_TOKEN not set; video embedding skipped")
        return None

    try:
        import replicate
    except ImportError:
        logger.warning("replicate package not installed; pip install replicate")
        return None

    path = Path(video_path)
    if not path.exists():
        logger.warning("Video file not found: %s", video_path)
        return None

    try:
        client = replicate.Client(api_token=EXTERNAL_PROVIDERS.replicate_api_token)
        with open(path, "rb") as f:
            output = client.run(
                model_ref,
                input={"video": f},
            )
        if output is None:
            return None
        if isinstance(output, dict) and "embeddings" in output:
            emb = output["embeddings"]
        elif isinstance(output, list):
            emb = output[0] if output else []
        else:
            emb = output if isinstance(output, list) else []
        if emb:
            return _pad_or_truncate(emb, VIDEO_DIM)
    except Exception as e:
        logger.warning("Replicate video embed failed: %s", e)
    return None
