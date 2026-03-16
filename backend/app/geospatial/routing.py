# app/geospatial/routing.py
import os
from typing import Any, Dict, Tuple

import aiohttp

from app.geospatial.geoutils import haversine_meters

MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
OSRM_URL = os.getenv("OSRM_URL")
ROUTING_PROVIDER = os.getenv("ROUTING_PROVIDER", "mapbox")


async def get_route_mapbox(
    start: Tuple[float, float], end: Tuple[float, float], profile: str = "driving"
) -> Dict[str, Any]:
    """Mapbox Directions API; expects lon,lat."""
    url = (
        f"https://api.mapbox.com/directions/v5/mapbox/{profile}"
        f"/{start[1]},{start[0]};{end[1]},{end[0]}"
    )
    params = {
        "geometries": "geojson",
        "overview": "full",
        "access_token": MAPBOX_TOKEN,
        "alternatives": "false",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            return await resp.json()


async def get_route_osrm(
    start: Tuple[float, float], end: Tuple[float, float], profile: str = "car"
) -> Dict[str, Any]:
    """OSRM route; expects lon,lat."""
    url = f"{OSRM_URL}/route/v1/{profile}/{start[1]},{start[0]};{end[1]},{end[0]}"
    params = {"overview": "full", "geometries": "geojson"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            return await resp.json()


async def get_eta_seconds(
    start: Tuple[float, float], end: Tuple[float, float], profile: str = "driving"
) -> int:
    if ROUTING_PROVIDER == "mapbox" and MAPBOX_TOKEN:
        data = await get_route_mapbox(start, end, profile=profile)
        if data.get("routes"):
            return int(data["routes"][0]["duration"])
    if ROUTING_PROVIDER == "osrm" and OSRM_URL:
        data = await get_route_osrm(start, end, profile=profile)
        if data.get("routes"):
            return int(data["routes"][0]["duration"])
    # Fallback: haversine / assumed average driving speed ~36 km/h
    d = haversine_meters(start[0], start[1], end[0], end[1])
    return int(d / 10.0)


async def get_isochrone_mapbox(
    center: Tuple[float, float], minutes: int = 10, profile: str = "driving"
) -> Dict[str, Any]:
    if not MAPBOX_TOKEN:
        raise ValueError("MAPBOX_TOKEN required for isochrone")
    lon, lat = center[1], center[0]
    url = f"https://api.mapbox.com/isochrone/v1/mapbox/{profile}/{lon},{lat}"
    params = {
        "contours_minutes": minutes,
        "polygons": "true",
        "access_token": MAPBOX_TOKEN,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            return await resp.json()
