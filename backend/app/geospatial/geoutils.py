# app/geospatial/geoutils.py
import math
from typing import Tuple


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance between two WGS84 points in meters."""
    R = 6_371_000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def bbox_from_point(
    lat: float, lon: float, radius_m: float
) -> Tuple[float, float, float, float]:
    """Approximate bbox in WGS84 degrees; accurate enough for small radii."""
    lat_deg = radius_m / 111_320.0
    lon_deg = radius_m / (111_320.0 * math.cos(math.radians(lat)))
    return (lat - lat_deg, lon - lon_deg, lat + lat_deg, lon + lon_deg)
