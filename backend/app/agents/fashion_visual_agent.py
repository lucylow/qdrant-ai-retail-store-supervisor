"""
Visual fashion search agent: photo → CLIP embedding → Qdrant fashion_clip search.
For "show me dresses like this [photo]" with filters (stock_status, price_max, category).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from app.config import FASHION_CLIP_COLLECTION, MODELS

# Lazy CLIP to avoid loading at import time
_clip_model = None


def _get_clip():
    global _clip_model
    if _clip_model is None:
        from sentence_transformers import SentenceTransformer
        _clip_model = SentenceTransformer(MODELS.image_embedding_model)
    return _clip_model


class VisualFashionAgent:
    """Photo → 70K Fashion-MNIST visual matches via Qdrant fashion_clip collection."""

    def __init__(self, qdrant_client: Any) -> None:
        self.qdrant = qdrant_client
        self.collection_name = FASHION_CLIP_COLLECTION

    def _encode_image(self, image_path: str) -> List[float]:
        from PIL import Image
        clip = _get_clip()
        img = Image.open(image_path).convert("RGB")
        vec = clip.encode(img, convert_to_numpy=True)
        if not isinstance(vec, np.ndarray):
            vec = np.array(vec, dtype=np.float32)
        return vec.flatten().tolist()

    def _encode_image_bytes(self, image_bytes: bytes) -> List[float]:
        import io
        from PIL import Image
        clip = _get_clip()
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        vec = clip.encode(img, convert_to_numpy=True)
        if not isinstance(vec, np.ndarray):
            vec = np.array(vec, dtype=np.float32)
        return vec.flatten().tolist()

    def visual_search(
        self,
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        score_threshold: float = 0.75,
        top_k: int = 8,
    ) -> Dict[str, Any]:
        """
        Run visual search on fashion_clip collection.
        Provide either image_path or image_bytes.
        filters: optional { "stock_status": "in_stock", "price_max": 200, "category": "Dress" }
        """
        if image_path is not None:
            query_vector = self._encode_image(image_path)
        elif image_bytes is not None:
            query_vector = self._encode_image_bytes(image_bytes)
        else:
            return {
                "visual_matches": 0,
                "top_matches": [],
                "avg_similarity": 0.0,
                "error": "Provide image_path or image_bytes",
            }

        conditions: List[Any] = []
        if filters:
            from qdrant_client.http import models as qmodels
            if filters.get("stock_status"):
                conditions.append(
                    qmodels.FieldCondition(
                        key="stock_status",
                        match=qmodels.MatchValue(value=filters["stock_status"]),
                    )
                )
            if filters.get("price_max") is not None:
                conditions.append(
                    qmodels.FieldCondition(
                        key="price",
                        range=qmodels.Range(lt=float(filters["price_max"])),
                    )
                )
            if filters.get("category"):
                conditions.append(
                    qmodels.FieldCondition(
                        key="category",
                        match=qmodels.MatchValue(value=str(filters["category"])),
                    )
                )

        query_filter = None
        if conditions:
            from qdrant_client.http import models as qmodels
            query_filter = qmodels.Filter(must=conditions)

        try:
            results = self.qdrant.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                vector_name="image",
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
            )
        except Exception as e:
            return {
                "visual_matches": 0,
                "top_matches": [],
                "avg_similarity": 0.0,
                "error": str(e),
            }

        top = results[:top_k]
        scores = [float(r.score or 0.0) for r in results]
        avg_sim = float(np.mean(scores)) if scores else 0.0

        top_matches = [
            {
                "id": str(r.id),
                "category": (r.payload or {}).get("category", ""),
                "price": (r.payload or {}).get("price"),
                "stock_status": (r.payload or {}).get("stock_status", ""),
                "similarity": round(float(r.score or 0.0), 3),
                "style": (r.payload or {}).get("style", ""),
                "color": (r.payload or {}).get("color", ""),
            }
            for r in top
        ]

        return {
            "visual_matches": len(results),
            "top_matches": top_matches,
            "avg_similarity": round(avg_sim, 3),
        }


__all__ = ["VisualFashionAgent"]
