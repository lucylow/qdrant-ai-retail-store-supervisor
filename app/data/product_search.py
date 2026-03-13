"""
Filtered product search and Qdrant Recommend API for Shopper + Inventory.

- search_products_filtered: vector + must/should/must_not (stock, region, price).
- recommend_products: item-to-item or episodic boosting (positive/negative IDs or vectors).
"""

from __future__ import annotations

import logging
from typing import Any, Sequence

from app.config import COLLECTIONS
from app.embeddings import embed_single
from app.qdrant_client import get_qdrant_client

logger = logging.getLogger(__name__)

COLL_PRODUCTS: str = COLLECTIONS.products


def _build_product_filter(
    *,
    stock_gt: int | None = None,
    region: str | None = None,
    price_lte: float | None = None,
    price_gte: float | None = None,
    category: str | None = None,
    exclude_skus: Sequence[str] | None = None,
) -> Any:
    """Build Qdrant filter (must / should / must_not) for products."""
    from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

    must = []
    must_not = []
    if stock_gt is not None:
        must.append(FieldCondition(key="stock", range=Range(gt=stock_gt)))
    if region is not None:
        must.append(FieldCondition(key="region", match=MatchValue(value=region)))
    # Prefer price_eur (matches inventory payload); fallback price
    if price_lte is not None:
        must.append(FieldCondition(key="price_eur", range=Range(lte=price_lte)))
    if price_gte is not None:
        must.append(FieldCondition(key="price_eur", range=Range(gte=price_gte)))
    if category is not None:
        must.append(FieldCondition(key="category", match=MatchValue(value=category)))
    if exclude_skus:
        for sku in exclude_skus:
            must_not.append(FieldCondition(key="sku", match=MatchValue(value=sku)))
    if not must and not must_not:
        return None
    return Filter(must=must, must_not=must_not if must_not else None)


def search_products_filtered(
    query: str | list[float],
    limit: int = 12,
    *,
    stock_gt: int | None = None,
    region: str | None = None,
    price_lte: float | None = None,
    price_gte: float | None = None,
    category: str | None = None,
    exclude_skus: Sequence[str] | None = None,
    hnsw_ef: int | None = None,
) -> list[dict[str, Any]]:
    """
    Vector search on products with payload filters (Shopper: stock>0, region, price).
    query: search text (will be embedded) or precomputed vector.
    """
    client = get_qdrant_client()
    if isinstance(query, str):
        qvec = embed_single(query).vectors[0].tolist()
    else:
        qvec = query
    query_filter = _build_product_filter(
        stock_gt=stock_gt,
        region=region,
        price_lte=price_lte,
        price_gte=price_gte,
        category=category,
        exclude_skus=exclude_skus,
    )
    params = None
    if hnsw_ef is not None:
        from qdrant_client.http import models as rest
        params = rest.SearchParams(hnsw_ef=hnsw_ef)
    hits = client.search(
        collection_name=COLL_PRODUCTS,
        query_vector=qvec,
        limit=limit,
        query_filter=query_filter,
        with_payload=True,
        params=params,
    )
    return [{"id": h.id, "score": h.score, "payload": h.payload or {}} for h in hits]


def recommend_products(
    positive: Sequence[dict[str, Any]],
    negative: Sequence[dict[str, Any]] | None = None,
    limit: int = 10,
    query_filter: Any = None,
    strategy: str | None = "average_vector",
) -> list[dict[str, Any]]:
    """
    Qdrant Recommend API: get products similar to positive examples and not negative.
    positive/negative: list of {"id": point_id} or {"vector": [float]}.
    Use in Inventory to expand candidates from episodic positives.
    """
    from qdrant_client.http import models as rest

    client = get_qdrant_client()
    neg = list(negative) if negative else []
    kwargs: dict[str, Any] = {
        "collection_name": COLL_PRODUCTS,
        "positive": list(positive),
        "negative": neg,
        "limit": limit,
        "query_filter": query_filter,
        "with_payload": True,
    }
    if strategy:
        try:
            kwargs["strategy"] = getattr(rest.RecommendStrategy, strategy.upper(), rest.RecommendStrategy.AVERAGE_VECTOR)
        except (AttributeError, TypeError):
            pass
    hits = client.recommend(**kwargs)
    return [{"id": h.id, "score": h.score, "payload": h.payload or {}} for h in hits]


__all__ = ["search_products_filtered", "recommend_products"]
