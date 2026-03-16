"""Performance metrics and Prometheus export."""
from __future__ import annotations

from app.performance.metrics import PerformanceMetrics, get_metrics


def test_metrics_record_latency() -> None:
    m = PerformanceMetrics(window_size=100)
    m.record_latency(100.0, True, "shopper")
    m.record_latency(800.0, True, "inventory")
    m.record_latency(50.0, False, "pricing")
    assert m._request_count == 3
    assert m._error_count == 1
    assert m.p95_latency_ms >= 0


def test_cache_hit_rate() -> None:
    m = PerformanceMetrics()
    m.record_cache_hit()
    m.record_cache_hit()
    m.record_cache_miss()
    assert m.cache_hit_rate == 2 / 3


def test_get_metrics_singleton() -> None:
    a = get_metrics()
    b = get_metrics()
    assert a is b
