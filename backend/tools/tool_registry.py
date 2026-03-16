from typing import Callable, Dict, List, Optional


class ToolRegistry:
    """
    Simple in-memory registry for dynamically built tools.
    """

    def __init__(self) -> None:
        self.tools: Dict[str, Callable] = {}

    def register(self, name: str, func: Callable) -> None:
        self.tools[name] = func

    def get(self, name: str) -> Optional[Callable]:
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        return list(self.tools.keys())

