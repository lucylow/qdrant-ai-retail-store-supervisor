#!/usr/bin/env python3
"""
Seed sample Migros stores for geospatial/live-map demo.
Run: DATABASE_URL=postgresql://postgres:postgres@localhost:5432/livemap python scripts/seed_migros_stores.py
Apply migrations/002_create_geodb.sql first.
"""
import asyncio
import os

import asyncpg

SAMPLE_STORES = [
    {
        "store_id": "migros_zurich_hauptbahnhof",
        "tenant_id": "migros",
        "name": "Migros Bahnhof Zürich",
        "address": "Bahnhofplatz 1",
        "city": "Zürich",
        "postcode": "8001",
        "lat": 47.378177,
        "lon": 8.540192,
        "categories": ["supermarket", "bakery"],
        "capabilities_text": "Large Migros in Zurich HB; fresh bakery; long opening hours",
        "capacity": 200,
    },
    {
        "store_id": "migros_zurich_seefeld",
        "tenant_id": "migros",
        "name": "Migros Seefeld",
        "address": "Seefeldstrasse 45",
        "city": "Zürich",
        "postcode": "8008",
        "lat": 47.3465,
        "lon": 8.5609,
        "categories": ["supermarket"],
        "capabilities_text": "Neighborhood Migros, small fresh produce section",
        "capacity": 80,
    },
    {
        "store_id": "migros_geneva_centre",
        "tenant_id": "migros",
        "name": "Migros Genève Centre",
        "address": "Rue du Centre 3",
        "city": "Genève",
        "postcode": "1201",
        "lat": 46.2044,
        "lon": 6.1432,
        "categories": ["supermarket"],
        "capabilities_text": "City center Migros with express checkout",
        "capacity": 150,
    },
]


async def seed() -> None:
    db_url = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/livemap"
    )
    conn = await asyncpg.connect(db_url)
    for s in SAMPLE_STORES:
        await conn.execute(
            """
            INSERT INTO stores (
                store_id, tenant_id, name, address, city, postcode,
                lat, lon, geom, categories, capabilities_text, capacity
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8,
                    ST_SetSRID(ST_MakePoint($8, $7), 4326)::geography,
                    $9, $10, $11)
            ON CONFLICT (store_id, tenant_id) DO UPDATE SET
                name = EXCLUDED.name,
                address = EXCLUDED.address,
                city = EXCLUDED.city,
                postcode = EXCLUDED.postcode,
                lat = EXCLUDED.lat,
                lon = EXCLUDED.lon,
                geom = EXCLUDED.geom,
                categories = EXCLUDED.categories,
                capabilities_text = EXCLUDED.capabilities_text,
                capacity = EXCLUDED.capacity
            """,
            s["store_id"],
            s["tenant_id"],
            s["name"],
            s["address"],
            s["city"],
            s["postcode"],
            s["lat"],
            s["lon"],
            s["categories"],
            s["capabilities_text"],
            s["capacity"],
        )
    await conn.close()
    print(f"Seeded {len(SAMPLE_STORES)} Migros stores.")


if __name__ == "__main__":
    asyncio.run(seed())
