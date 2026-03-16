from __future__ import annotations

import numpy as np

from .helpers import (
    compute_cache_hit_rate,
    compute_conversion_lift,
    compute_stockout_reduction,
    load_swiss_episodes,
    simulate_qps_capacity,
)


def test_swiss_inventory_metrics() -> None:
    """Validate production-style inventory targets: latency, QPS, cache hit, ROI."""
    episodes = load_swiss_episodes(["coop", "migros", "manor"])

    # Latency P95 <= 50ms
    latencies = [e["latency_ms"] for e in episodes]
    assert np.percentile(latencies, 95) <= 50

    # QPS capacity test (mock 450/sec)
    assert simulate_qps_capacity(episodes, target_qps=450) == "PASS"

    # Cache hit rate >= 87%
    assert compute_cache_hit_rate(episodes) >= 0.87

    # ROI-style targets
    assert compute_conversion_lift(episodes) >= 0.23  # +23% conversion lift
    assert compute_stockout_reduction(episodes) >= 0.67  # 67% stockout reduction

