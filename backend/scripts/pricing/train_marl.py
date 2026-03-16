#!/usr/bin/env python3
"""MARL training pipeline for dynamic pricing agents."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.rl.training_env import RetailPricingEnvironment
from app.rl.agent_policies import get_policies_for_agents
from app.rl.reward_functions import RewardWeights
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents", type=int, default=5)
    parser.add_argument("--episodes", type=int, default=1000)
    parser.add_argument("--products", type=int, default=100)
    parser.add_argument("--quick", action="store_true", help="Short run for demo")
    args = parser.parse_args()

    if args.quick:
        args.episodes = 50
        args.products = 20

    env = RetailPricingEnvironment(n_agents=args.agents, n_products=args.products)
    policies = get_policies_for_agents(args.agents, state_dim=8, action_dim=args.products)

    total_rewards: list[float] = []
    for ep in range(args.episodes):
        obs = env.reset()
        ep_reward = 0.0
        step = 0
        while step < min(100, env.max_steps):
            policy_list = list(policies.values())
            actions = {}
            for i, agent in enumerate(env.agents):
                state_flat = obs[i].mean(axis=0)
                policy = policy_list[i % len(policy_list)]
                out = policy.act(state_flat)
                actions[agent] = np.broadcast_to(out.action, args.products)
            obs, rewards, done, _ = env.step(actions)
            ep_reward += sum(rewards.values())
            step += 1
            if done:
                break
        total_rewards.append(ep_reward)
        if (ep + 1) % 10 == 0:
            logger.info("Episode %d mean reward %.2f", ep + 1, np.mean(total_rewards[-10:]))

    logger.info("Training complete. Final 10-episode mean reward: %.2f", np.mean(total_rewards[-10:]))
    print("MARL training complete. Run streamlit run demo/dynamic_pricing.py for live dashboard.")


if __name__ == "__main__":
    main()
