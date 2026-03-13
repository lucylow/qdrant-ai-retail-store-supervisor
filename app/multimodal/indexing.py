"""
Video product indexing: extract keyframes + audio, encode to 4 named vectors, upsert to Qdrant.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.multimodal.encoders import MultimodalProductEncoders, extract_audio_from_video
from app.multimodal.schema import (
    PRODUCTS_MULTIMODAL_COLLECTION,
    get_products_multimodal_vectors_config,
)

logger = logging.getLogger(__name__)


def ensure_products_multimodal_collection(client: Any) -> None:
    """Create products_multimodal collection with 4 named vectors if not exists."""
    try:
        client.get_collection(PRODUCTS_MULTIMODAL_COLLECTION)
        logger.debug("Collection %s already exists", PRODUCTS_MULTIMODAL_COLLECTION)
    except Exception:
        client.create_collection(
            collection_name=PRODUCTS_MULTIMODAL_COLLECTION,
            vectors_config=get_products_multimodal_vectors_config(),
        )
        logger.info("Created collection %s", PRODUCTS_MULTIMODAL_COLLECTION)


def index_video_product(
    client: Any,
    sku: str,
    video_file: str,
    metadata: Dict[str, Any],
    *,
    encoders: Optional[MultimodalProductEncoders] = None,
    every_nth_frame: int = 5,
    audio_path_override: Optional[str] = None,
) -> None:
    """
    Index one product with video: extract keyframes + audio, encode to textvector, imagevector, audiovector, videovector.

    metadata should include at least "title", "desc"; optional "image" (path to product photo).
    """
    encoders = encoders or MultimodalProductEncoders()
    video_path = Path(video_file)
    if not video_path.exists():
        raise FileNotFoundError(video_file)

    # Text: title + desc
    title = metadata.get("title", "")
    desc = metadata.get("desc", metadata.get("description", ""))
    text_vec = encoders.encode_text(f"{title} {desc}")

    # Image: product photo if provided
    image_path = metadata.get("image")
    image_vec = encoders.encode_image(image_path) if image_path and Path(image_path).exists() else None
    if image_vec is None:
        # Placeholder so point has all 4 vectors
        import numpy as np
        from app.multimodal.schema import IMAGE_DIM
        image_vec = [0.0] * IMAGE_DIM

    # Video: keyframes → CLIP → average pool
    video_vec = encoders.encode_video_file(str(video_path), every_nth_frame=every_nth_frame)

    # Audio: extract from video (or use override path) then encode
    audio_path = audio_path_override or extract_audio_from_video(str(video_path))
    audio_vec = encoders.encode_audio(audio_path=audio_path) if audio_path else encoders.encode_audio()

    # Payload
    payload = {**metadata, "sku": sku}
    try:
        import subprocess
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            payload["video_duration"] = float(result.stdout.strip())
    except Exception:
        payload["video_duration"] = 0.0

    # Qdrant accepts str or int point ids
    point_id = str(sku) if not isinstance(sku, int) else sku

    vectors = {
        "textvector": text_vec,
        "imagevector": image_vec,
        "audiovector": audio_vec,
        "videovector": video_vec,
    }
    from qdrant_client.http import models as qmodels
    point = qmodels.PointStruct(id=point_id, vector=vectors, payload=payload)
    client.upsert(collection_name=PRODUCTS_MULTIMODAL_COLLECTION, points=[point])
    logger.info("Indexed video product %s (%s vectors)", sku, len(vectors))


def index_product_vectors(
    client: Any,
    sku: str,
    vectors: Dict[str, List[float]],
    payload: Dict[str, Any],
) -> None:
    """Upsert a product point with precomputed named vectors (e.g. text + image only, no video)."""
    ensure_products_multimodal_collection(client)
    point_id = str(sku) if not isinstance(sku, int) else sku
    from qdrant_client.http import models as qmodels
    point = qmodels.PointStruct(id=point_id, vector=vectors, payload={**payload, "sku": str(sku)})
    client.upsert(collection_name=PRODUCTS_MULTIMODAL_COLLECTION, points=[point])
