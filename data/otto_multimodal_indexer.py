"""
Batch index OTTO sessions into Qdrant with 4 named vectors per session.

Usage:
  python data/otto_multimodal_indexer.py --input data/otto/sessions.parquet --qdrant-url http://localhost:6333 --batch-size 1000 [--max-sessions 50000]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Run from repo root so qdrant package is importable
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    import polars as pl
except ImportError:
    pl = None

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels
except ImportError:
    QdrantClient = None
    qmodels = None

from qdrant.multimodal_otto_sessions import OttoMultimodalVectorizer, get_otto_sessions_vectors_config

COLLECTION_OTTO_SESSIONS = "otto_sessions"


def ensure_collection(client: QdrantClient) -> None:
    try:
        client.get_collection(COLLECTION_OTTO_SESSIONS)
    except Exception:
        client.create_collection(
            collection_name=COLLECTION_OTTO_SESSIONS,
            vectors_config=get_otto_sessions_vectors_config(),
        )
        print(f"Created collection {COLLECTION_OTTO_SESSIONS}")


def run(
    input_path: str,
    qdrant_url: str,
    batch_size: int = 1000,
    max_sessions: int | None = None,
) -> None:
    if pl is None or QdrantClient is None or qmodels is None:
        raise RuntimeError("polars and qdrant-client required")
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(input_path)

    df = pl.read_parquet(path)
    if max_sessions is not None and df.height > max_sessions:
        df = df.head(max_sessions)
    print(f"Indexing {df.height} sessions to {qdrant_url} (batch_size={batch_size})")

    vectorizer = OttoMultimodalVectorizer()
    client = QdrantClient(url=qdrant_url)
    ensure_collection(client)

    # Map column names from process_otto output
    cols = df.columns
    aid_col = "aids" if "aids" in cols else "aid_list"
    type_col = "event_types" if "event_types" in cols else "types"
    ts_col = "ts_list" if "ts_list" in cols else "ts"

    points_batch: list = []
    for i, row in enumerate(df.iter_rows(named=True)):
        session = row.get("session", "")
        aids = row.get(aid_col, [])
        event_types = row.get(type_col, [])
        ts_list = row.get(ts_col, [])
        if hasattr(aids, "to_list"):
            aids = aids.to_list()
        if hasattr(event_types, "to_list"):
            event_types = event_types.to_list()
        if hasattr(ts_list, "to_list"):
            ts_list = ts_list.to_list()
        conversion_success = "order" in (event_types or [])
        ts_vals = list(ts_list) if ts_list else [0]
        duration = max(ts_vals) - min(ts_vals) if len(ts_vals) > 1 else 0

        point_id, vectors, payload = vectorizer.vectorize_session_row({
            "session": session,
            "aids": aids,
            "event_types": event_types,
            "ts_list": ts_list,
            "conversion_success": conversion_success,
            "session_duration_ms": duration,
        })
        points_batch.append(
            qmodels.PointStruct(
                id=point_id,
                vector=vectors,
                payload=payload,
            )
        )
        if len(points_batch) >= batch_size:
            client.upsert(collection_name=COLLECTION_OTTO_SESSIONS, points=points_batch)
            points_batch = []
            print(f"  Indexed {i + 1}/{df.height}")
    if points_batch:
        client.upsert(collection_name=COLLECTION_OTTO_SESSIONS, points=points_batch)
    print(f"Done. {df.height} sessions → 4 vectors each in {COLLECTION_OTTO_SESSIONS}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/otto/sessions.parquet", help="sessions.parquet path")
    parser.add_argument("--qdrant-url", default="http://localhost:6333", help="Qdrant URL")
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--max-sessions", type=int, default=None)
    args = parser.parse_args()
    run(
        input_path=args.input,
        qdrant_url=args.qdrant_url,
        batch_size=args.batch_size,
        max_sessions=args.max_sessions,
    )


if __name__ == "__main__":
    main()
