from typing import List


class SupervisorAgent:
    """
    Lightweight supervisor that maps questions to relevant tools/agents.
    """

    def decide_tools(self, question: str) -> List[str]:
        q = question.lower()

        if "inventory" in q or "stock" in q:
            return ["inventory_risk_analyzer"]

        if "bundle" in q or "cross-sell" in q:
            return ["bundle_recommender"]

        if "price" in q or "pricing" in q:
            return ["price_optimizer"]

        if "campaign" in q or "promotion" in q or "promo" in q:
            return ["marketing_campaign_builder"]

        return []

