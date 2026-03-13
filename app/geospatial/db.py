# app/geospatial/db.py
import os
from typing import Any, List, Optional

import asyncpg

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/livemap"
)
_pool: Optional[asyncpg.Pool] = None


async def init_db_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
    return _pool


async def fetch(query: str, *args: Any) -> List[asyncpg.Record]:
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(query, *args)


async def fetchrow(query: str, *args: Any) -> Optional[asyncpg.Record]:
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, *args)


async def execute(query: str, *args: Any) -> str:
    pool = await init_db_pool()
    async with pool.acquire() as conn:
        return await conn.execute(query, *args)
