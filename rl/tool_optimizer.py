
rom __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, Optional


class ToolUsageOptimizer:
    """
    Tracks simple statistics about tool usefulness and learns which tools
    work best for a given context length.
    """

    def __init__(self) -> None:
        # key: tool name, value: running average reward
        self._tool_stats: Dict[str, float] = defaultdict(float)
        self._tool_counts: Dict[str, int] = defaultdict(int)

    def choose_tool(self, tools: Iterable[str], context: str) -> Optional[str]:
        """
        Pick the tool with the best historical reward; fall back to longest
        context heuristic as in the prompt if we have no stats.
        """
        tools = list(tools)
        if not tools:
            return None

        # if we have learned stats, use them
        best: Optional[str] = None
        best_score = float("-inf")

        for tool in tools:
            count = self._tool_counts.get(tool, 0)
            if count > 0:
                score = self._tool_stats[tool]
            else:
                # exploration prior
                score = len(context)

            if score > best_score:
                best_score = score
                best = tool

        return best

    def record_outcome(self, tool: str, reward: float, alpha: float = 0.1) -> None:
        """
        Update running average reward for a tool (simple bandit update).
        """
        prev = self._tool_stats.get(tool, 0.0)
        updated = (1 - alpha) * prev + alpha * reward
        self._tool_stats[tool] = updated
        self._tool_counts[tool] += 1

