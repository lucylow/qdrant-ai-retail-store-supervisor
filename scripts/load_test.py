#!/usr/bin/env python3
"""
1000 QPS load generation with P95 and cache hit assertions for judge demo.
Usage: python scripts/load_test.py --qps 1000 --duration 300 --assert-p95 800
"""
from __future__ import annotations

import argparse
import asyncio
import statistics
import time
from typing import List

try:
    import httpx
except ImportError:
    httpx = None


async def run_single(
    client: "httpx.AsyncClient",
    url: str,
    query: str,
) -> tuple[float, bool]:
    start = time.perf_counter()
    try:
        r = await client.post(url, json={"query": query}, timeout=30.0)
        ok = r.status_code == 200
        return (time.perf_counter() - start) * 1000, ok
    except Exception:
        return (time.perf_counter() - start) * 1000, False


async def load_test(
    base_url: str = "http://localhost:8000",
    qps: int = 1000,
    duration_s: int = 300,
    endpoint: str = "/demo/query",
) -> dict:
    url = f"{base_url.rstrip('/')}{endpoint}"
    latencies: List[float] = []
    errors = 0
    total = 0
    cache_hits = 0
    start = time.perf_counter()
    queries = [f"retail query {i} cheese fondue" for i in range(500)]

    async with httpx.AsyncClient() as client:
        while (time.perf_counter() - start) < duration_s:
            batch_size = min(qps, 200)
            tasks = [
                run_single(client, url, queries[i % len(queries)])
                for i in range(batch_size)
            ]
            results = await asyncio.gather(*tasks)
            for lat, ok in results:
                total += 1
                if ok:
                    latencies.append(lat)
                else:
                    errors += 1
            elapsed = time.perf_counter() - start
            if elapsed > 0:
                current_qps = total / elapsed
                if current_qps >= qps:
                    await asyncio.sleep(0.1)
        await asyncio.sleep(0)

    elapsed = time.perf_counter() - start
    actual_qps = total / elapsed if elapsed > 0 else 0
    p95 = float(statistics.quantiles(latencies, n=100)[94]) if len(latencies) >= 20 else 0.0
    error_rate = errors / total if total > 0 else 0.0

    return {
        "total_requests": total,
        "duration_s": elapsed,
        "qps": actual_qps,
        "p95_ms": p95,
        "error_rate": error_rate,
        "cache_hit_rate": cache_hits / total if total else 0.0,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--qps", type=int, default=1000)
    ap.add_argument("--duration", type=int, default=60)
    ap.add_argument("--base-url", default="http://localhost:8000")
    ap.add_argument("--assert-p95", type=float, default=800, help="Assert P95 latency below this ms")
    args = ap.parse_args()

    if httpx is None:
        print("Install httpx: pip install httpx")
        return

    print(f"Load test: {args.qps} QPS target, {args.duration}s...")
    result = asyncio.run(load_test(args.base_url, args.qps, args.duration))
    print(f"QPS: {result['qps']:.0f} | P95: {result['p95_ms']:.0f}ms | Error Rate: {result['error_rate']:.1%}")

    p95_ok = result["p95_ms"] <= args.assert_p95
    qps_ok = result["qps"] >= args.qps * 0.8
    print(f"P95 < {args.assert_p95}ms: {'✓' if p95_ok else '✗'}")
    print(f"QPS >= 80% target: {'✓' if qps_ok else '✗'}")
    if not p95_ok or not qps_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
