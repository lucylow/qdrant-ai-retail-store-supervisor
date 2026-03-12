from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from qdrant_client.http import models as rest

from app.qdrant.production_client import ProductionQdrantClient


@dataclass
class HardNegativeTriplet:
    query: str
    positive: str
    hard_negative: str


async def mine_hard_negatives(
    client: ProductionQdrantClient,
    limit: int = 1000,
) -> List[HardNegativeTriplet]:
    """
    Illustrative hard‑negative mining loop.

    We treat `retail_goals` as queries and pull solutions from a
    `retail_solutions` collection.
    """
    from qdrant_client.http import models as models  # local alias

    triplets: List[HardNegativeTriplet] = []

    goals = client.scroll(
        collection_name="retail_goals",
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="confidence",
                    range=models.Range(lt=0.3),
                )
            ]
        ),
        limit=limit,
    )

    for goal in goals:
        payload = goal.payload or {}
        query = str(payload.get("query") or payload.get("text") or "")
        if not query:
            continue

        positive_res: Sequence[rest.ScoredPoint] = client.client.search(
            collection_name="retail_solutions",
            query_vector=goal.vector,
            limit=1,
            score_threshold=None,
        )
        if not positive_res:
            continue
        positive = str((positive_res[0].payload or {}).get("text", ""))

        hard_neg_res: Sequence[rest.ScoredPoint] = client.client.search(
            collection_name="retail_solutions",
            query_vector=goal.vector,
            limit=1,
            score_threshold=0.7,
        )
        if not hard_neg_res:
            continue
        hard_negative = str((hard_neg_res[0].payload or {}).get("text", ""))

        triplets.append(HardNegativeTriplet(query, positive, hard_negative))

    return triplets


__all__ = ["HardNegativeTriplet", "mine_hard_negatives"]

