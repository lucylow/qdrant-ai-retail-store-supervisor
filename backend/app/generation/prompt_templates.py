from typing import List

SYSTEM = (
    "You are an expert retail assistant. Use only the provided context passages to answer questions. "
    "Cite any facts with [n] where n is the passage index. If you cannot answer from the context, say so."
)

TEMPLATE = """
{system}

CONTEXT:
{context}

QUESTION:
{question}

Answer concisely (<=200 words), with citations like [0], [1] for facts.
"""


def build_prompt(
    question: str,
    contexts: List[str],
    system: str = SYSTEM,
    max_contexts: int = 5,
) -> str:
    ctx = "\n\n".join(f"[{i}] {c}" for i, c in enumerate(contexts[:max_contexts]))
    return TEMPLATE.format(system=system, context=ctx, question=question)
