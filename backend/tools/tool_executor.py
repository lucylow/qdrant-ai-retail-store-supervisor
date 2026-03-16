from typing import Any, Callable


class ToolExecutor:
    """
    Simple execution wrapper for dynamically built tools.
    """

    def execute(self, tool: Callable[..., Any], data: Any) -> Any:
        return tool(data)

