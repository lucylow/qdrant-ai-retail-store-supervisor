"""
RetailRocket + Qdrant Discovery API demo.

POST /demo/discovery-recs: recommend by item_ids and context (co_purchased / co_carted / co_viewed).
"""

from __future__ import annotations

from typing import Any

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError:
    FastAPI = None
    HTTPException = None
    BaseModel = None  # type: ignore

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from app.services.retailrocket_discovery import RetailRocketDiscovery
except ImportError:
    RetailRocketDiscovery = None


if BaseModel is not None:

    class DiscoveryRecRequest(BaseModel):
        item_ids: list[int]
        context: str = "co_purchased"
else:
    DiscoveryRecRequest = None  # type: ignore


_discovery: RetailRocketDiscovery | None = None


def get_discovery() -> RetailRocketDiscovery:
    global _discovery
    if _discovery is None and RetailRocketDiscovery:
        _discovery = RetailRocketDiscovery(context_dir=ROOT / "data" / "retailrocket")
    if _discovery is None:
        raise HTTPException(status_code=503, detail="RetailRocketDiscovery not available")
    return _discovery


app = FastAPI(title="RetailRocket + Qdrant Discovery Demo", version="0.1.0")


@app.post("/demo/discovery-recs")
async def demo_discovery_recommendations(body: DiscoveryRecRequest | dict | None = None) -> dict[str, Any]:
    """Judge demo: RetailRocket → Discovery API recommendations."""
    if body is None:
        body = DiscoveryRecRequest(item_ids=[], context="co_purchased") if DiscoveryRecRequest else {"item_ids": [], "context": "co_purchased"}
    item_ids = body.item_ids if hasattr(body, "item_ids") else (body.get("item_ids") or [])
    context = body.context if hasattr(body, "context") else (body.get("context") or "co_purchased")
    if not item_ids:
        return {
            "input_items": [],
            "context": context,
            "recommendations": [],
            "avg_score": 0.0,
            "high_conv_items": 0,
            "retailrocket_source": "2.7M real events (view/add2cart/transaction)",
            "discovery_api": "Qdrant recommend API",
        }
    try:
        discovery = get_discovery()
    except HTTPException:
        return {
            "input_items": item_ids,
            "context": context,
            "recommendations": [],
            "avg_score": 0.0,
            "high_conv_items": 0,
            "retailrocket_source": "2.7M real events (view/add2cart/transaction)",
            "discovery_api": "Qdrant recommend API",
            "error": "Discovery service unavailable (Qdrant or context data missing)",
        }
    recs = discovery.discover_recommendations(
        item_ids, context=context, limit=12
    )
    scores = [r["score"] for r in recs]
    high_conv = len([r for r in recs if (r.get("conversion_rate") or 0) > 0.1])
    return {
        "input_items": item_ids,
        "context": context,
        "recommendations": recs,
        "avg_score": sum(scores) / len(scores) if scores else 0.0,
        "high_conv_items": high_conv,
        "retailrocket_source": "2.7M real events (view/add2cart/transaction)",
        "discovery_api": "Qdrant v1.10+ recommend API",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)
