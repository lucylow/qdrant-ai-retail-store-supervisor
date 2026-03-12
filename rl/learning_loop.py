from __future__ import annotations

from typing import Sequence

from rl.reward_model import RewardModel
from rl.rl_agent import RLAgent


class LearningLoop:
    """
    Thin wrapper that ties together:
    - RLAgent
    - RewardModel

    You can call `train_step` after each interaction to update the agent.
    """

    def __init__(self, agent: RLAgent, reward_model: RewardModel) -> None:
        self.agent = agent
        self.reward_model = reward_model

    def train_step(
        self,
        states: Sequence[Sequence[float]],
        actions: Sequence[int],
        answer_quality: float,
        retrieval_relevance: float,
        user_feedback: float,
    ) -> float:
        """
        Compute a single scalar reward and update the policy over a short
        trajectory (typically 1-step for bandit-style RAG decisions).
        """
        reward = self.reward_model.compute_reward(
            answer_quality,
            retrieval_relevance,
            user_feedback,
        )

        rewards = [reward for _ in actions]
        loss = self.agent.update_from_trajectory(states, actions, rewards)
        return loss

