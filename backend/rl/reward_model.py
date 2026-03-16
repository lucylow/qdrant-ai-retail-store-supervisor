from dataclasses import dataclass


@dataclass
class RewardModel:
    """
    Linear reward model combining:
    - answer_quality: e.g. human rating or automatic metric
    - retrieval_relevance: how good the retrieved docs were
    - user_feedback: explicit thumbs-up/down or engagement
    """

    answer_weight: float = 0.5
    retrieval_weight: float = 0.3
    feedback_weight: float = 0.2

    def compute_reward(
        self,
        answer_quality: float,
        retrieval_relevance: float,
        user_feedback: float,
    ) -> float:
        reward = (
            self.answer_weight * answer_quality
            + self.retrieval_weight * retrieval_relevance
            + self.feedback_weight * user_feedback
        )
        return float(reward)

