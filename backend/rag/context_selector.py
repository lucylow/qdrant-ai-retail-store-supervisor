import numpy as np
from typing import Any, Iterable, List


class ContextSelector:
    """
    Simple learnable scorer for retrieved documents.

    This starts with random weights and can be nudged via `update_weights`
    whenever you have a scalar reward signal for a chosen context set.
    """

    def __init__(self, feature_dim: int = 5) -> None:
        self.feature_dim = feature_dim
        # Initialize small random weights so we have exploration by default.
        self.weights = np.random.rand(feature_dim)

    def _features_for_doc(self, doc: Any) -> np.ndarray:
        """
        Very lightweight feature extractor.

        For now we just generate pseudo-features based on available metadata.
        You can plug in real features such as:
        - retrieval score
        - recency
        - click-through rate
        - document length
        """
        rng = np.random.default_rng(abs(hash(str(getattr(doc, "id", id(doc))))) % (2**32))
        return rng.random(self.feature_dim)

    def score_documents(self, docs: Iterable[Any], top_k: int = 3) -> List[Any]:
        """
        Rank documents and return the top_k for context.

        This matches the structure requested in the prompt, but also exposes
        a configurable `top_k`.
        """
        scored: List[tuple[float, Any]] = []
        for d in docs:
            features = self._features_for_doc(d)
            score = float(np.dot(self.weights, features))
            scored.append((score, d))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in scored[:top_k]]

    def update_weights(self, docs: Iterable[Any], reward: float, lr: float = 0.01) -> None:
        """
        Very simple policy-gradient-style update:

        - Compute average feature vector over selected docs.
        - Move weights in direction of reward * features.
        """
        features: List[np.ndarray] = [self._features_for_doc(d) for d in docs]
        if not features:
            return
        avg_feat = np.mean(features, axis=0)
        self.weights += lr * reward * avg_feat

