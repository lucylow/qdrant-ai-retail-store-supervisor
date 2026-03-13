from typing import List, Dict, Any, Union
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import logging

logger = logging.getLogger(__name__)
BATCH_SIZE = 128


def upsert_named_vector_point(
    client: QdrantClient,
    collection_name: str,
    point_id: Union[str, int],
    vectors: Dict[str, List[float]],
    payload: Dict[str, Any],
) -> None:
    """Upsert a single point with named vectors (e.g. textvector, imagevector, audiovector, videovector)."""
    point = PointStruct(id=point_id, vector=vectors, payload=payload)
    client.upsert(collection_name=collection_name, points=[point])
    logger.debug("Upserted point %s to %s with %d vectors", point_id, collection_name, len(vectors))


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

