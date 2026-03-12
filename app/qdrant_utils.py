from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import logging

logger = logging.getLogger(__name__)
BATCH_SIZE = 128


def upsert_points(
    client: QdrantClient,
    collection_name: str,
    vectors: List[List[float]],
    payloads: List[Dict[str, Any]],
    ids: List[str],
) -> None:
    assert len(vectors) == len(payloads) == len(ids)
    for i in range(0, len(ids), BATCH_SIZE):
        j = min(i + BATCH_SIZE, len(ids))
        points = [
            PointStruct(id=ids[k], vector=vectors[k], payload=payloads[k])
            for k in range(i, j)
        ]
        client.upsert(collection_name=collection_name, points=points)
        logger.debug("Upserted %d points to %s", j - i, collection_name)

