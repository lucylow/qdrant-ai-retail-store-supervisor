from __future__ import annotations

from typing import Sequence

import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim

from rl.policy_network import PolicyNetwork


class RLAgent:
    """
    Lightweight policy-gradient agent controlling:
    - retrieval strategies
    - context selection strategies
    - tool usage modes
    """

    def __init__(
        self,
        state_dim: int = 128,
        action_dim: int = 10,
        lr: float = 1e-3,
        exploration_eps: float = 0.1,
    ) -> None:
        self.policy = PolicyNetwork(state_dim=state_dim, action_dim=action_dim)

        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)
        self.exploration_eps = exploration_eps

    def select_action(self, state: Sequence[float]) -> int:
        """
        Epsilon-greedy over the policy logits.
        """
        state_tensor = torch.tensor(np.array(state), dtype=torch.float32).unsqueeze(0)
        logits = self.policy(state_tensor)

        if np.random.rand() < self.exploration_eps:
            # exploration
            return int(np.random.randint(logits.shape[-1]))

        action = torch.argmax(logits, dim=-1).item()
        return int(action)

    def update_from_trajectory(
        self,
        states: Sequence[Sequence[float]],
        actions: Sequence[int],
        rewards: Sequence[float],
        gamma: float = 0.99,
    ) -> float:
        """
        REINFORCE-style update over a short trajectory.
        """
        if not states:
            return 0.0

        states_tensor = torch.tensor(np.array(states), dtype=torch.float32)
        actions_tensor = torch.tensor(actions, dtype=torch.long)
        rewards_tensor = torch.tensor(rewards, dtype=torch.float32)

        # compute discounted returns
        returns = []
        g = 0.0
        for r in reversed(rewards_tensor.tolist()):
            g = r + gamma * g
            returns.append(g)
        returns = torch.tensor(list(reversed(returns)), dtype=torch.float32)
        if returns.std() > 0:
            returns = (returns - returns.mean()) / (returns.std() + 1e-8)

        logits = self.policy(states_tensor)
        log_probs = F.log_softmax(logits, dim=-1)
        chosen_log_probs = log_probs[range(len(actions_tensor)), actions_tensor]

        loss = -(chosen_log_probs * returns).mean()

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return float(loss.item())

