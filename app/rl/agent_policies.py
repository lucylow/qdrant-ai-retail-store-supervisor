"""Actor-critic style policies per agent type (pricing agents)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np


@dataclass
class PolicyOutput:
    """Action and value from a single agent policy."""
    action: np.ndarray
    log_prob: float
    value: float
    raw_action: float  # price multiplier in [-0.2, 0.2]


class ActorCriticPolicy:
    """Simple deterministic policy: state -> price multiplier."""

    def __init__(self, state_dim: int, action_dim: int = 1, hidden: int = 64):
        self.state_dim = state_dim
        self.action_dim = action_dim
        # Small random weights for demo (replace with trained nets)
        self._W1 = np.random.randn(state_dim, hidden) * 0.1
        self._W2 = np.random.randn(hidden, action_dim) * 0.1
        self._value_W = np.random.randn(hidden, 1) * 0.1

    def act(self, state: np.ndarray) -> PolicyOutput:
        """Return action (price multiplier) and value."""
        if state.ndim == 1:
            state = state.reshape(1, -1)
        h = np.tanh(state @ self._W1)
        raw = float(np.tanh((h @ self._W2).flatten()[0]))
        raw = np.clip(raw, -0.2, 0.2)
        action = np.array([raw], dtype=np.float32)
        value = float(h @ self._value_W)
        return PolicyOutput(
            action=action,
            log_prob=0.0,
            value=value,
            raw_action=raw,
        )


def get_policies_for_agents(
    n_agents: int, state_dim: int, action_dim: int = 1
) -> Dict[str, ActorCriticPolicy]:
    """One policy per agent type (market, demand, margin, competitor, supervisor)."""
    names = [
        "market_monitor",
        "demand_forecaster",
        "margin_optimizer",
        "competitor_response",
        "pricing_supervisor",
    ]
    return {
        names[i % len(names)]: ActorCriticPolicy(state_dim, action_dim)
        for i in range(n_agents)
    }
