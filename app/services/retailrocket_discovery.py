"""
Qdrant Discovery-style recommendations from RetailRocket events.

Uses 2.7M events to drive recommend API: co-viewed, co-carted, co-purchased
patterns. Recommend by positive item IDs (with optional precomputed context).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels
except ImportError:
    QdrantClient = None  # type: ignore
    qmodels = None

try:
    import polars as pl
except ImportError:
    pl = None

COLLECTION_ITEMS = "retailrocket_items"
CONTEXT_CO_PURCHASED = "co_purchased"
CONTEXT_CO_CARTED = "co_carted"
CONTEXT_CO_VIEWED = "co_viewed"


class RetailRocketDiscovery:
    """Real-time recommendations from RetailRocket patterns via Qdrant recommend API."""

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        context_dir: Path | str | None = None,
    ):
        self.client = QdrantClient(url=qdrant_url) if QdrantClient else None
        self._context_dir = Path(context_dir or "data/retailrocket")
        self._co_purchased: pl.DataFrame | None = None
        self._co_carted: pl.DataFrame | None = None
        self._co_viewed: pl.DataFrame | None = None

    def _load_context(self, context: str) -> pl.DataFrame | None:
        if pl is None:
            return None
        path = self._context_dir / f"discovery_{context}.parquet"
        if not path.exists():
            return None
        return pl.read_parquet(path)

    def _get_related_ids(self, item_ids: list[int], context: str, limit: int = 20) -> list[str]:
        """Resolve related item IDs from precomputed co-occurrence (for recommend positive set)."""
        if context == CONTEXT_CO_PURCHASED:
            df = self._co_purchased or self._load_context("co_purchased")
        elif context == CONTEXT_CO_CARTED:
            df = self._co_carted or self._load_context("co_carted")
        elif context == CONTEXT_CO_VIEWED:
            df = self._co_viewed or self._load_context("co_viewed")
        else:
            df = None
        if df is None or df.is_empty():
            return [str(i) for i in item_ids]
        out: list[str] = []
        for iid in item_ids:
            if "itemid_a" in df.columns and "itemid_b" in df.columns:
                filtered = df.filter(pl.col("itemid_a") == iid).head(limit)
                if not filtered.is_empty():
                    out.extend(str(x) for x in filtered.get_column("itemid_b").to_list())
        if not out:
            out = [str(i) for i in item_ids]
        return list(dict.fromkeys(out))[: limit * 3]

    def discover_recommendations(
        self,
        item_ids: list[int],
        context: str = CONTEXT_CO_PURCHASED,
        limit: int = 10,
        score_threshold: float | None = None,
    ) -> list[dict[str, Any]]:
        """Qdrant recommend API: real-time recs from RetailRocket patterns."""
        if not self.client or not qmodels:
            return []
        positive = [str(i) for i in item_ids]
        # Optionally expand positive set from co-occurrence
        related = self._get_related_ids(item_ids, context, limit=5)
        if len(related) > len(positive):
            positive = list(dict.fromkeys(related + positive))[:30]
        try:
            results = self.client.recommend(
                collection_name=COLLECTION_ITEMS,
                positive=positive,
                limit=limit,
                with_payload=True,
                score_threshold=score_threshold,
            )
        except Exception:
            return []
        out = []
        for r in results:
            raw_id = r.id
            try:
                itemid = int(raw_id) if raw_id is not None else 0
            except (TypeError, ValueError):
                itemid = 0
            payload = r.payload or {}
            out.append({
                "itemid": itemid,
                "title": payload.get("catname", ""),
                "score": getattr(r, "score", 0.0),
                "conversion_rate": payload.get("view_to_cart_rate", 0.0),
                "context": context,
            })
        return out


def build_discovery_contexts(events_path: Path, out_dir: Path, max_events: int | None = None) -> None:
    """Build co-viewed, co-carted, co-purchased parquet tables from events for Discovery."""
    if pl is None:
        raise RuntimeError("polars required")
    out_dir.mkdir(parents=True, exist_ok=True)
    if events_path.suffix == ".parquet":
        events = pl.read_parquet(events_path)
    else:
        events = pl.read_csv(events_path, try_parse_dates=True, infer_schema_length=100_000)
    if "event" not in events.columns or "visitorid" not in events.columns or "itemid" not in events.columns:
        raise ValueError("events must have columns: event, visitorid, itemid")
    if max_events is not None and len(events) > max_events:
        events = events.head(max_events)
    for event_type, out_name in [
        ("view", "co_viewed"),
        ("add2cart", "co_carted"),
        ("transaction", "co_purchased"),
    ]:
        ev = events.filter(pl.col("event") == event_type)
        if ev.is_empty():
            continue
        session_items = ev.group_by("visitorid").agg(pl.col("itemid").alias("items"))
        rows = []
        for r in session_items.iter_rows(named=True):
            items = r.get("items")
            if items is None:
                continue
            if hasattr(items, "to_list"):
                ids = items.to_list()
            elif isinstance(items, list):
                ids = items
            else:
                ids = list(items)
            ids = [int(x) for x in ids if x is not None]
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    a, b = ids[i], ids[j]
                    if a != b:
                        rows.append({"itemid_a": a, "itemid_b": b})
                        rows.append({"itemid_a": b, "itemid_b": a})
        if not rows:
            continue
        df = pl.DataFrame(rows)
        df.write_parquet(out_dir / f"discovery_{out_name}.parquet")
        print(f"Wrote {out_name}: {len(df)} pairs")
