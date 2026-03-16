from typing import Dict, List


class ContextBuilder:
    """
    Builds enriched context strings for retail reasoning.

    Includes simple document ranking and compression to keep prompts manageable.
    """

    def build_context(
        self,
        question: str,
        product_data: List[Dict],
        sales_data: List[Dict],
        retrieved_docs: List,
        max_docs: int = 10,
        max_chars: int = 6000,
    ) -> str:
        """
        `retrieved_docs` can be either:
        - raw payload dicts containing "text"
        - Qdrant ScoredPoint objects with `.payload` and optional `.score`
        """
        # Rank docs by score when available, otherwise keep order
        docs_normalized: List[Dict] = []
        for d in retrieved_docs:
            if hasattr(d, "payload"):
                score = getattr(d, "score", None)
                docs_normalized.append(
                    {
                        "text": d.payload.get("text", ""),
                        "score": score,
                    }
                )
            else:
                docs_normalized.append(
                    {
                        "text": d.get("text", ""),
                        "score": None,
                    }
                )

        # Sort by score descending when present
        docs_normalized.sort(
            key=lambda x: (x["score"] is not None, x["score"]),
            reverse=True,
        )

        # Limit number of docs
        docs_normalized = docs_normalized[:max_docs]

        context_parts: List[str] = []
        context_parts.append("QUESTION:")
        context_parts.append(question)

        context_parts.append("\nPRODUCT DATA:")
        for p in product_data:
            context_parts.append(str(p))

        context_parts.append("\nSALES DATA:")
        for s in sales_data:
            context_parts.append(str(s))

        context_parts.append("\nKNOWLEDGE BASE:")
        for doc in docs_normalized:
            text = doc["text"]
            if not text:
                continue
            context_parts.append(text)

        full_context = "\n".join(context_parts)

        # Simple context compression: truncate if overly long
        if len(full_context) > max_chars:
            full_context = full_context[: max_chars - 500] + "\n...[truncated context]..."

        return full_context

