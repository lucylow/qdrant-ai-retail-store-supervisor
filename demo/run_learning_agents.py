from __future__ import annotations

"""
Simple demo script that exercises:
- Agentic RAG retrieval
- LLM-based retail reasoning
"""

from copilot.retail_copilot import RetailCopilot


def main() -> None:
    copilot = RetailCopilot()

    question = "Which products should we promote this week?"

    response = copilot.answer(question)

    print("QUESTION:")
    print(question)
    print("\nANSWER:")
    print(response)


if __name__ == "__main__":
    main()

