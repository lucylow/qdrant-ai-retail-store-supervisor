"""Revenue, margin, and market-share reward functions for MARL pricing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np


@dataclass
class RewardWeights:
    revenue: float = 0.5
    margin: float = 0.3
    market_share: float = 0.2
    inventory_efficiency: float = 0.1


def revenue_reward(price: float, demand: float) -> float:
    """Reward = price * demand (revenue)."""
    return float(price * demand)


def margin_reward(price: float, cost: float, demand: float) -> float:
    """Reward = (price - cost) * demand, normalized."""
    if price <= 0:
        return 0.0
    margin = (price - cost) / price
    return float(margin * demand)


def market_share_reward(our_demand: float, total_demand: float) -> float:
    """Share of total market demand."""
    if total_demand <= 0:
        return 0.0
    return float(our_demand / total_demand)


def inventory_efficiency_reward(used: float, available: float) -> float:
    """Reward for not over/under stocking (target ~80% utilization)."""
    if available <= 0:
        return 0.0
    utilization = used / available
    target = 0.8
    return float(1.0 - abs(utilization - target))


def compute_agent_reward(
    revenue: float,
    market_share: float,
    inventory_efficiency: float,
    margin_pct: float = 0.25,
    weights: Optional[RewardWeights] = None,
) -> float:
    """Multi-objective reward for a single agent."""
    w = weights or RewardWeights()
    r = w.revenue * np.tanh(revenue / 1000.0)
    r += w.margin * margin_pct
    r += w.market_share * market_share
    r += w.inventory_efficiency * inventory_efficiency
    return float(r)
