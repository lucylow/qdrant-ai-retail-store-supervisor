import logging
from typing import Dict, Any

from app.agents.interfaces import safe_execute, timed

logger = logging.getLogger(__name__)


class AnalyticsAgent:
    name = "AnalyticsAgent"

    @safe_execute
    @timed
    def run(self, context: Dict[str, Any]):
        sols = context.get("solutions") or []
        metrics: Dict[str, Any] = {"num_solutions": len(sols)}
        confs = [s.get("confidence") for s in sols if s.get("confidence") is not None]
        if confs:
            metrics["avg_confidence"] = sum(confs) / len(confs)
        else:
            metrics["avg_confidence"] = None
        return {"metrics": metrics}

