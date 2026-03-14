"""MADDPG-style multi-agent RL orchestration for pricing."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from app.rl.agent_policies import ActorCriticPolicy, get_policies_for_agents
from app.rl.training_env import RetailPricingEnvironment

logger = logging.getLogger(__name__)


@dataclass
class MARLAction:
    """Output of MARL supervisor for a single SKU."""
    base_price: float
    confidence: float
    revenue_lift_pct: float
    price_multiplier: float


class PricingMARLSupervisor:
    """MARL orchestration: aggregate 5 agent policies into one pricing action."""

    def __init__(self, n_agents: int = 5, state_dim: int = 8):
        self.n_agents = n_agents
        self.state_dim = state_dim
        self.policies = get_policies_for_agents(n_agents, state_dim)
        self._env: Optional[RetailPricingEnvironment] = None

    def _build_state_single(
        self,
        sku: str,
        competitor_prices: List[float],
        elasticity: float,
    ) -> np.ndarray:
        """Build state vector for one SKU (length state_dim)."""
        state = np.zeros(self.state_dim, dtype=np.float32)
        state[0] = np.mean(competitor_prices) if competitor_prices else 35.0
        state[1] = np.std(competitor_prices) if competitor_prices else 0.0
        state[2] = elasticity
        state[3] = 0.5
        state[4] = 1.0 if "tshirt" in sku.lower() else 0.0
        state[5] = 1.0 if "jeans" in sku.lower() else 0.0
        state[6] = 1.0 if "dress" in sku.lower() else 0.0
        state[7] = min(competitor_prices) if competitor_prices else 35.0
        return state

    async def act(
        self,
        state: Dict[str, Any] | np.ndarray,
        sku: str = "",
        competitor_prices: Optional[List[float]] = None,
        elasticity: float = -1.5,
    ) -> MARLAction:
        """Compute MARL action from state (sync implementation, async for API)."""
        if isinstance(state, dict):
            comp = state.get("competitor_prices") or competitor_prices or [35.0]
            el = state.get("elasticity", elasticity)
            sku = state.get("sku", sku)
        else:
            comp = competitor_prices or [35.0]
            el = elasticity
        s = self._build_state_single(sku, comp, el)

        # Aggregate actions from all agent policies
        multipliers: List[float] = []
        values: List[float] = []
        for name, policy in self.policies.items():
            out = policy.act(s)
            multipliers.append(out.raw_action)
            values.append(out.value)

        agg_mult = float(np.clip(np.median(multipliers), -0.2, 0.2))
        base_price = float(np.mean(comp)) * (1.0 + agg_mult) if comp else 35.0
        confidence = float(np.clip(0.5 + np.mean(values) * 0.01, 0.1, 0.99))
        revenue_lift_pct = float(agg_mult * 100 * 1.5)  # heuristic lift from multiplier

        return MARLAction(
            base_price=round(base_price, 2),
            confidence=confidence,
            revenue_lift_pct=revenue_lift_pct,
            price_multiplier=agg_mult,
        )
