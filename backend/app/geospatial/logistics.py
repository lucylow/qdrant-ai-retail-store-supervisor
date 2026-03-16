# app/geospatial/logistics.py
import uuid
from typing import Any, Dict, List, Tuple

from app.geospatial.db import execute, fetch, fetchrow
from app.geospatial.geoutils import haversine_meters
from app.geospatial.routing import get_eta_seconds


async def get_stores_needing_restock(
    threshold: int = 20, tenant_id: str = "migros"
) -> List[Dict[str, Any]]:
    """Stores with total inventory below threshold (for restock routing)."""
    rows = await fetch(
        """
        SELECT s.store_id, s.tenant_id, s.name, s.lat, s.lon, COALESCE(SUM(i.quantity), 0)::int AS qty
        FROM stores s
        LEFT JOIN inventory i ON i.store_id = s.store_id AND i.tenant_id = s.tenant_id
        WHERE s.tenant_id = $1
        GROUP BY s.store_id, s.tenant_id, s.name, s.lat, s.lon
        HAVING COALESCE(SUM(i.quantity), 0) < $2
        """,
        tenant_id,
        threshold,
    )
    return [dict(r) for r in rows]


def _euclid_distance(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return haversine_meters(a[0], a[1], b[0], b[1])


async def greedy_vehicle_routes(
    depot: Tuple[float, float],
    stores: List[Dict[str, Any]],
    vehicle_count: int = 2,
    capacity: int = 500,
) -> List[Dict[str, Any]]:
    """
    Simple greedy clustering: assign nearest unvisited store to each vehicle until capacity.
    Returns list of route dicts: {vehicle_id, route: [{store_id, lat, lon, eta_s}]}.
    """
    unvisited = list(stores)
    routes: List[Dict[str, Any]] = []
    for v in range(vehicle_count):
        veh_id = f"veh_{v + 1}"
        pos = depot
        used = 0
        route: List[Dict[str, Any]] = []
        while unvisited and used < capacity:
            nearest = min(
                unvisited,
                key=lambda s: _euclid_distance((s["lat"], s["lon"]), pos),
            )
            try:
                eta = await get_eta_seconds(pos, (nearest["lat"], nearest["lon"]))
            except Exception:
                eta = int(
                    _euclid_distance(pos, (nearest["lat"], nearest["lon"])) / 10.0
                )
            route.append(
                {
                    "store_id": nearest["store_id"],
                    "lat": nearest["lat"],
                    "lon": nearest["lon"],
                    "eta_s": eta,
                }
            )
            unvisited.remove(nearest)
            pos = (nearest["lat"], nearest["lon"])
            used += 100
        routes.append({"vehicle_id": veh_id, "route": route})
    return routes


async def create_and_persist_routes(
    depot: Tuple[float, float],
    vehicle_count: int = 2,
    capacity: int = 500,
    tenant_id: str = "migros",
) -> List[Dict[str, Any]]:
    stores = await get_stores_needing_restock(tenant_id=tenant_id)
    if not stores:
        return []
    routes = await greedy_vehicle_routes(depot, stores, vehicle_count, capacity)
    for r in routes:
        rid = "route_" + uuid.uuid4().hex[:8]
        await execute(
            """
            INSERT INTO vehicle_routes(route_id, tenant_id, vehicle_id, route_order, capacity_total, capacity_used)
            VALUES($1, $2, $3, $4, $5, $6)
            """,
            rid,
            tenant_id,
            r["vehicle_id"],
            r["route"],
            capacity,
            0,
        )
    return routes
