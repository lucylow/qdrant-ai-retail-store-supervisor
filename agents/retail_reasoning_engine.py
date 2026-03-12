from typing import Any, Dict, List, Sequence

from agents.inventory_agent import InventoryAgent
from agents.merchandising_agent import MerchandisingAgent
from agents.marketing_agent import MarketingAgent
from agents.pricing_agent import PricingAgent
from agents.supervisor_agent import SupervisorAgent
from tools.tool_registry import ToolRegistry
from agents.tool_builder_agent import ToolBuilderAgent
from app.rl_metrics import RLMetricsLogger
from rl.learning_loop import LearningLoop
from rl.reward_model import RewardModel
from rl.rl_agent import RLAgent
from rl.tool_optimizer import ToolUsageOptimizer


class RetailReasoningEngine:
    """
    Coordinates multi-agent collaboration and dynamic tool usage.

    This version integrates RL so that:
    - task decomposition is guided by a learnable policy
    - tool selection is adapted over time based on rewards
    """

    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self.supervisor = SupervisorAgent()
        self.inventory_agent = InventoryAgent()
        self.merchandising_agent = MerchandisingAgent()
        self.marketing_agent = MarketingAgent()
        self.pricing_agent = PricingAgent()
        self.tool_builder = ToolBuilderAgent()
        self.registry = registry or ToolRegistry()

        # RL components
        self.rl_agent = RLAgent()
        self.reward_model = RewardModel()
        self.learning_loop = LearningLoop(self.rl_agent, self.reward_model)
        self.tool_optimizer = ToolUsageOptimizer()
        self.metrics_logger = RLMetricsLogger()

        self._bootstrap_default_tools()

    # --- Tool bootstrapping ---

    def _bootstrap_default_tools(self) -> None:
        """
        Register a few canonical tools that can be selected by the supervisor.
        """
        self.registry.register(
            "inventory_risk_analyzer", self.tool_builder.build_inventory_risk_tool()
        )
        self.registry.register(
            "bundle_recommender", self.tool_builder.build_bundle_tool()
        )

    # --- State encoding for RL ---

    def _encode_state(
        self,
        question: str,
        products: List[Dict[str, Any]],
        inventory: List[Dict[str, Any]],
        sales: List[Dict[str, Any]],
    ) -> List[float]:
        """
        Very compact hand-crafted state vector (length <= 128).
        """
        q = question.lower()
        features: List[float] = []

        # Domain keyword features
        features.extend(
            [
                float(any(k in q for k in ["inventory", "stock", "replenish"])),
                float(any(k in q for k in ["bundle", "cross-sell", "upsell"])),
                float(any(k in q for k in ["campaign", "promotion", "promo"])),
                float(any(k in q for k in ["price", "pricing", "margin"])),
            ]
        )

        # Simple scale features
        features.extend(
            [
                min(len(products), 100) / 100.0,
                min(len(inventory), 100) / 100.0,
                min(len(sales), 100) / 100.0,
            ]
        )

        # Pad to 16 dims, RLAgent expects 128; the policy network handles
        # smaller state_dim, but we aim for a consistent length here.
        while len(features) < 16:
            features.append(0.0)

        return features

    # --- Learned task decomposition + coordination ---

    def _learned_subtasks(self, action: int) -> List[str]:
        """
        Map discrete actions to subtask sets.
        """
        mapping = {
            0: ["analyze_inventory_risk"],
            1: ["suggest_merchandising_bundles"],
            2: ["generate_marketing_campaigns"],
            3: ["optimize_pricing"],
            4: ["analyze_inventory_risk", "suggest_merchandising_bundles"],
            5: ["generate_marketing_campaigns", "optimize_pricing"],
            6: ["analyze_inventory_risk", "optimize_pricing"],
        }
        return mapping.get(action, ["general_retail_insight"])

    def _select_tools(self, question: str, context: str) -> List[str]:
        """
        Combine legacy supervisor heuristics with RL tool optimizer.
        """
        candidate_tools = self.supervisor.decide_tools(question)
        chosen = self.tool_optimizer.choose_tool(candidate_tools, context)
        return [chosen] if chosen else candidate_tools

    def run(
        self,
        question: str,
        products: List[Dict[str, Any]],
        inventory: List[Dict[str, Any]],
        sales: List[Dict[str, Any]],
        answer_quality: float | None = None,
        retrieval_relevance: float | None = None,
        user_feedback: float | None = None,
    ) -> Dict[str, Any]:
        """
        High-level orchestration: choose tools and domain agents, execute, and
        return structured outputs.

        Optional feedback signals can be passed in to update the RL policy.
        """
        # Encode state and choose an action
        state = self._encode_state(question, products, inventory, sales)
        action = self.rl_agent.select_action(state)
        subtasks = self._learned_subtasks(action)

        # Context proxy (could be replaced with actual RAG context)
        context_repr = f"q_len={len(question)}, products={len(products)}, sales={len(sales)}"
        selected_tools = self._select_tools(question, context_repr)

        results: Dict[str, Any] = {
            "question": question,
            "selected_tools": selected_tools,
            "subtasks": subtasks,
            "insights": {},
            "rl_action": action,
        }

        # Inventory intelligence
        if "analyze_inventory_risk" in subtasks:
            results["insights"]["inventory_risk"] = self.inventory_agent.detect_stock_risk(
                inventory
            )

        # Merchandising
        if "suggest_merchandising_bundles" in subtasks:
            results["insights"]["bundles"] = self.merchandising_agent.suggest_bundles(
                products
            )

        # Marketing
        if "generate_marketing_campaigns" in subtasks and products:
            # For now, just create a campaign for the first product
            results["insights"]["campaign"] = self.marketing_agent.create_campaign(
                products[0]
            )

        # Pricing
        if "optimize_pricing" in subtasks and products:
            # Naive demand proxy from sales volume
            demand = min(1.0, max(0.0, len(sales) / 100.0))
            optimized = []
            for p in products:
                optimized.append(
                    {
                        "product": p.get("name", ""),
                        "original_price": p.get("price"),
                        "optimized_price": self.pricing_agent.optimize_price(p, demand),
                    }
                )
            results["insights"]["pricing"] = optimized

        # Dynamic tool usage if any tools selected
        dynamic_tool_results: Dict[str, Any] = {}
        for tool_name in selected_tools:
            tool = self.registry.get(tool_name)
            if not tool:
                continue
            if tool_name == "inventory_risk_analyzer":
                dynamic_tool_results[tool_name] = tool(inventory)
            elif tool_name == "bundle_recommender":
                dynamic_tool_results[tool_name] = tool(products)

        if dynamic_tool_results:
            results["insights"]["dynamic_tools"] = dynamic_tool_results

        # --- RL update and metrics logging (if feedback provided) ---
        if (
            answer_quality is not None
            and retrieval_relevance is not None
            and user_feedback is not None
        ):
            reward = self.reward_model.compute_reward(
                answer_quality, retrieval_relevance, user_feedback
            )
            # 1-step trajectory: [state], [action], [reward]
            self.learning_loop.train_step(
                states=[state],
                actions=[action],
                answer_quality=answer_quality,
                retrieval_relevance=retrieval_relevance,
                user_feedback=user_feedback,
            )
            self.metrics_logger.log(
                answer_quality=answer_quality,
                retrieval_relevance=retrieval_relevance,
                user_feedback=user_feedback,
                reward=reward,
            )

            # Update tool-level bandit stats
            for tool_name in selected_tools:
                self.tool_optimizer.record_outcome(tool_name, reward)

            results["rl_reward"] = reward
            results["rl_metrics"] = self.metrics_logger.averages()

        return results


