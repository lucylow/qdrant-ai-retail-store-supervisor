"""Multi-agent RL environment for retail dynamic pricing."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np

try:
    import gym
    from gym import spaces

    _HAS_GYM = True
except ImportError:
    gym = None  # type: ignore
    spaces = None  # type: ignore
    _HAS_GYM = False

from app.rl.reward_functions import compute_agent_reward


class RetailPricingEnvironment:
    """Multi-agent RL environment for dynamic pricing (gym-like)."""

    def __init__(self, n_agents: int = 5, n_products: int = 100):
        self.n_agents = n_agents
        self.n_products = n_products
        self.agents = [f"agent_{i}" for i in range(n_agents)]
        self.current_step = 0
        self.max_steps = 365 * 24

        self._state: Optional[np.ndarray] = None
        self._competitor_prices = np.random.uniform(25, 45, (n_agents, n_products))
        self._inventory = np.random.uniform(50, 200, (n_agents, n_products))
        self._base_prices = np.random.uniform(28, 42, n_products)

        if _HAS_GYM and spaces is not None:
            self.observation_space = spaces.Box(
                low=0, high=np.inf, shape=(n_agents, n_products, 8)
            )
            self.action_space = spaces.Box(
                low=-0.2, high=0.2, shape=(n_products,)
            )
        else:
            self.observation_space = None
            self.action_space = None

    def reset(self) -> np.ndarray:
        """Reset env; return initial observations."""
        self.current_step = 0
        self._competitor_prices = np.random.uniform(25, 45, (self.n_agents, self.n_products))
        self._inventory = np.random.uniform(50, 200, (self.n_agents, self.n_products))
        return self._get_observations()

    def _get_observations(self) -> np.ndarray:
        """Build observation tensor (n_agents, n_products, 8)."""
        obs = np.zeros((self.n_agents, self.n_products, 8))
        for i in range(self.n_agents):
            obs[i, :, 0] = self._base_prices
            obs[i, :, 1] = self._competitor_prices[i]
            obs[i, :, 2] = self._inventory[i]
            obs[i, :, 3] = np.mean(self._competitor_prices, axis=0)
            obs[i, :, 4] = self.current_step / self.max_steps
            obs[i, :, 5] = np.std(self._competitor_prices, axis=0)
            obs[i, :, 6] = 1.0
            obs[i, :, 7] = 0.5
        self._state = obs
        return obs

    def _apply_price_actions(self, actions: Dict[str, np.ndarray]) -> np.ndarray:
        """Apply per-agent price multipliers -> (n_agents, n_products)."""
        prices = np.zeros((self.n_agents, self.n_products))
        for i, agent in enumerate(self.agents):
            act = actions.get(agent, np.zeros(self.n_products))
            if act.size != self.n_products:
                act = np.broadcast_to(act, self.n_products) if act.size else np.zeros(self.n_products)
            multipliers = 1.0 + np.clip(act, -0.2, 0.2)
            prices[i] = self._base_prices * multipliers
        return prices

    def _compute_demands(self, prices: np.ndarray) -> np.ndarray:
        """Simple demand model: elasticity -1.5 vs competitor avg."""
        comp_avg = np.mean(self._competitor_prices, axis=0)
        elasticity = -1.5
        demand = 100 * (prices / (comp_avg + 1e-6)) ** elasticity
        return np.clip(demand, 0, self._inventory)

    def _compute_revenues(self, prices: np.ndarray, demands: np.ndarray) -> Dict[str, float]:
        """Total revenue per agent."""
        revenues = {}
        for i, agent in enumerate(self.agents):
            revenues[agent] = float(np.sum(prices[i] * demands[i]))
        return revenues

    def _compute_market_share(self, agent_idx: int, demands: np.ndarray) -> float:
        total = np.sum(demands)
        return float(np.sum(demands[agent_idx]) / total) if total > 0 else 0.0

    def _inventory_score(self, agent_idx: int, demands: np.ndarray) -> float:
        used = np.sum(demands[agent_idx])
        avail = np.sum(self._inventory[agent_idx])
        if avail <= 0:
            return 0.0
        util = used / avail
        return float(1.0 - abs(util - 0.8))

    def step(
        self, actions: Dict[str, np.ndarray]
    ) -> tuple[np.ndarray, Dict[str, float], bool, Dict[str, Any]]:
        """Execute one step; return obs, rewards, done, info."""
        prices = self._apply_price_actions(actions)
        demands = self._compute_demands(prices)
        revenues = self._compute_revenues(prices, demands)

        rewards = {}
        for i, agent in enumerate(self.agents):
            margin_pct = 0.25
            rewards[agent] = compute_agent_reward(
                revenue=revenues[agent],
                market_share=self._compute_market_share(i, demands),
                inventory_efficiency=self._inventory_score(i, demands),
                margin_pct=margin_pct,
            )

        self.current_step += 1
        done = self.current_step >= self.max_steps
        return self._get_observations(), rewards, done, {"revenues": revenues}


# Alias for gym.Env if gym is available
if _HAS_GYM and gym is not None:

    class RetailPricingGymEnv(gym.Env):
        """Gym wrapper for RetailPricingEnvironment."""

        def __init__(self, n_agents: int = 5, n_products: int = 100):
            super().__init__()
            self._env = RetailPricingEnvironment(n_agents, n_products)
            self.observation_space = self._env.observation_space
            self.action_space = self._env.action_space

        def reset(self, *args, **kwargs):
            return self._env.reset()

        def step(self, actions):
            return self._env.step(actions)
