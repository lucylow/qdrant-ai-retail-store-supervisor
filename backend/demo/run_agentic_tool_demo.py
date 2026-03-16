from agents.tool_builder_agent import ToolBuilderAgent
from tools.tool_executor import ToolExecutor


def main() -> None:
    builder = ToolBuilderAgent()
    executor = ToolExecutor()

    # Build an inventory risk analyzer tool dynamically
    tool = builder.build_inventory_risk_tool()

    inventory = [
        {"id": 1, "name": "Jacket", "stock": 5, "reorder_point": 10},
        {"id": 2, "name": "Gloves", "stock": 20, "reorder_point": 10},
    ]

    result = executor.execute(tool, inventory)
    print("Inventory risk output:", result)


if __name__ == "__main__":
    main()

