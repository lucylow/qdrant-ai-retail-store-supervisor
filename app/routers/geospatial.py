# app/routers/geospatial.py
"""Geospatial mapping, navigation & logistics API (Migros retail stores)."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, WebSocket
from pydantic import BaseModel

from app.geospatial.db import fetch, fetchrow, execute
from app.geospatial.routing import (
    get_eta_seconds,
    get_route_mapbox,
    get_route_osrm,
    get_isochrone_mapbox,
    ROUTING_PROVIDER,
    MAPBOX_TOKEN,
    OSRM_URL,
)
from app.geospatial.ws_manager import ws_manager
from app.geospatial.eta_cache import get_eta_cache, set_eta_cache
from app.geospatial.logistics import create_and_persist_routes

router = APIRouter(prefix="/api", tags=["Geospatial"])


# ---------- Models ----------


class StoreOut(BaseModel):
    store_id: str
    tenant_id: Optional[str] = None
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    lat: float
    lon: float
    categories: List[str] = []
    capabilities_text: Optional[str] = None
    capacity: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class ETAQuery(BaseModel):
    from_lat: float
    from_lon: float
    to_store_id: str
    profile: Optional[str] = "driving"
    intent_id: Optional[str] = None  # for ETA cache (livemap integration)


class RouteQuery(BaseModel):
    from_lat: float
    from_lon: float
    to_store_id: str
    profile: Optional[str] = "driving"


class PlanRequest(BaseModel):
    depot_lat: float
    depot_lon: float
    vehicle_count: int = 2
    capacity: int = 500
    tenant_id: Optional[str] = "migros"


# ---------- Store endpoints ----------


@router.get("/stores/nearby", response_model=List[StoreOut])
async def stores_nearby(
    lat: float = Query(...),
    lon: float = Query(...),
    radius_m: int = Query(1500, ge=50, le=50_000),
    limit: int = Query(50, le=200),
    tenant_id: str = Query("migros"),
) -> List[StoreOut]:
    """PostGIS ST_DWithin + order by distance."""
    sql = """
    SELECT store_id, tenant_id, name, address, city, postcode, lat, lon,
           categories, capabilities_text, capacity, metadata
    FROM stores
    WHERE tenant_id = $1
      AND ST_DWithin(
            geom::geography,
            ST_SetSRID(ST_Point($2, $3), 4326)::geography,
            $4
          )
    ORDER BY ST_Distance(geom::geography, ST_SetSRID(ST_Point($2, $3), 4326)::geography)
    LIMIT $5
    """
    rows = await fetch(sql, tenant_id, lon, lat, radius_m, limit)
    return [StoreOut(**dict(r)) for r in rows]


@router.get("/stores/bbox", response_model=List[StoreOut])
async def stores_bbox(
    min_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lat: float = Query(...),
    max_lon: float = Query(...),
    limit: int = Query(200, le=500),
    tenant_id: str = Query("migros"),
) -> List[StoreOut]:
    sql = """
    SELECT store_id, tenant_id, name, address, city, postcode, lat, lon,
           categories, capabilities_text, capacity, metadata
    FROM stores
    WHERE tenant_id = $1 AND lat BETWEEN $2 AND $4 AND lon BETWEEN $3 AND $5
    LIMIT $6
    """
    rows = await fetch(sql, tenant_id, min_lat, min_lon, max_lat, max_lon, limit)
    return [StoreOut(**dict(r)) for r in rows]


@router.get("/stores/{store_id}", response_model=StoreOut)
async def store_detail(
    store_id: str,
    tenant_id: str = Query("migros"),
) -> StoreOut:
    row = await fetchrow(
        """
        SELECT store_id, tenant_id, name, address, city, postcode, lat, lon,
               categories, capabilities_text, capacity, metadata
        FROM stores WHERE store_id = $1 AND tenant_id = $2
        """,
        store_id,
        tenant_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Store not found")
    return StoreOut(**dict(row))


# ---------- Routing ----------


@router.post("/routing/eta")
async def compute_eta(q: ETAQuery) -> Dict[str, Any]:
    if q.intent_id:
        cached = await get_eta_cache(q.intent_id, q.to_store_id)
        if cached is not None:
            return {"eta_seconds": cached.get("eta"), "cached": True}
    row = await fetchrow(
        "SELECT lat, lon FROM stores WHERE store_id = $1 AND tenant_id = 'migros'",
        q.to_store_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Store not found")
    start = (q.from_lat, q.from_lon)
    end = (float(row["lat"]), float(row["lon"]))
    secs = await get_eta_seconds(start, end, profile=q.profile or "driving")
    if q.intent_id:
        await set_eta_cache(q.intent_id, q.to_store_id, secs)
    return {"eta_seconds": secs, "cached": False}


@router.post("/routing/route")
async def route_for_store(q: RouteQuery) -> Dict[str, Any]:
    row = await fetchrow(
        "SELECT lat, lon FROM stores WHERE store_id = $1 AND tenant_id = 'migros'",
        q.to_store_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Store not found")
    start = (q.from_lat, q.from_lon)
    end = (float(row["lat"]), float(row["lon"]))
    if ROUTING_PROVIDER == "mapbox" and MAPBOX_TOKEN:
        route = await get_route_mapbox(start, end, profile=q.profile or "driving")
    elif ROUTING_PROVIDER == "osrm" and OSRM_URL:
        route = await get_route_osrm(start, end, profile="car")
    else:
        raise HTTPException(
            status_code=503,
            detail="No routing provider configured (MAPBOX_TOKEN or OSRM_URL)",
        )
    return route


@router.get("/routing/isochrone")
async def isochrone(
    lat: float = Query(...),
    lon: float = Query(...),
    minutes: int = Query(10, ge=1, le=60),
    profile: str = Query("driving"),
) -> Dict[str, Any]:
    try:
        iso = await get_isochrone_mapbox((lat, lon), minutes, profile=profile)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return iso


# ---------- Logistics ----------


@router.post("/logistics/plan")
async def plan_routes(req: PlanRequest) -> List[Dict[str, Any]]:
    depot = (req.depot_lat, req.depot_lon)
    routes = await create_and_persist_routes(
        depot,
        vehicle_count=req.vehicle_count,
        capacity=req.capacity,
        tenant_id=req.tenant_id or "migros",
    )
    return routes


# ---------- WebSocket ----------


@router.websocket("/ws/{channel}")
async def ws_endpoint(websocket: WebSocket, channel: str) -> None:
    await ws_manager.connect(channel, websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            await websocket.send_json({"echo": msg})
    except Exception:
        pass
    finally:
        await ws_manager.disconnect(channel, websocket)
