"""
Async metrics collection and Prometheus export for performance dashboard.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Deque, List

from collections import deque

try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


@dataclass
class LatencySample:
    latency_ms: float
    success: bool
    agent: str = ""


class PerformanceMetrics:
    """In-memory and optional Prometheus metrics for QPS, P95, cache hit, GPU."""

    def __init__(self, window_size: int = 10_000) -> None:
        self.window_size = window_size
        self._latencies: Deque[LatencySample] = deque(maxlen=window_size)
        self._cache_hits = 0
        self._cache_misses = 0
        self._request_count = 0
        self._error_count = 0
        self._agent_timings: Deque[dict] = deque(maxlen=window_size)
        self._start_time = time.monotonic()

        if PROMETHEUS_AVAILABLE:
            self._req_counter = Counter("perf_requests_total", "Total requests", ["agent"])
            self._latency_hist = Histogram(
                "perf_request_latency_seconds",
                "Request latency",
                ["agent"],
                buckets=(0.05, 0.1, 0.2, 0.5, 0.8, 1.0, 2.0, 5.0),
            )
            self._cache_hit_counter = Counter("perf_cache_hits_total", "Cache hits")
            self._cache_miss_counter = Counter("perf_cache_misses_total", "Cache misses")
            self._gpu_gauge = Gauge("perf_gpu_utilization_percent", "GPU utilization %")
        else:
            self._req_counter = self._latency_hist = None
            self._cache_hit_counter = self._cache_miss_counter = self._gpu_gauge = None

    def record_latency(self, latency_ms: float, success: bool = True, agent: str = "") -> None:
        self._latencies.append(LatencySample(latency_ms=latency_ms, success=success, agent=agent))
        self._request_count += 1
        if not success:
            self._error_count += 1
        if self._latency_hist and agent:
            self._latency_hist.labels(agent=agent).observe(latency_ms / 1000.0)
        if self._req_counter and agent:
            self._req_counter.labels(agent=agent).inc()

    def record_cache_hit(self) -> None:
        self._cache_hits += 1
        if self._cache_hit_counter:
            self._cache_hit_counter.inc()

    def record_cache_miss(self) -> None:
        self._cache_misses += 1
        if self._cache_miss_counter:
            self._cache_miss_counter.inc()

    def record_agent_timing(self, agent_name: str, start: float, end: float, success: bool) -> None:
        self._agent_timings.append({
            "agent_name": agent_name,
            "start": start,
            "end": end,
            "success": success,
        })

    def set_gpu_utilization(self, percent: float) -> None:
        if self._gpu_gauge is not None:
            self._gpu_gauge.set(percent)

    @property
    def qps(self) -> float:
        elapsed = time.monotonic() - self._start_time
        return self._request_count / elapsed if elapsed > 0 else 0.0

    @property
    def p95_latency_ms(self) -> float:
        if not self._latencies:
            return 0.0
        sorted_ms = sorted(s.latency_ms for s in self._latencies)
        idx = int(len(sorted_ms) * 0.95) - 1
        idx = max(0, idx)
        return sorted_ms[idx]

    @property
    def cache_hit_rate(self) -> float:
        total = self._cache_hits + self._cache_misses
        return self._cache_hits / total if total > 0 else 0.0

    @property
    def success_rate(self) -> float:
        return 1.0 - (self._error_count / self._request_count) if self._request_count > 0 else 1.0

    def agent_timings_snapshot(self) -> List[dict]:
        return list(self._agent_timings)


_metrics: PerformanceMetrics | None = None


def get_metrics() -> PerformanceMetrics:
    global _metrics
    if _metrics is None:
        _metrics = PerformanceMetrics()
    return _metrics
