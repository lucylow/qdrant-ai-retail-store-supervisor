from typing import Any, Dict, List


class RetailContextBuilder:
    """
    Simple retail-aware context builder.

    This is intentionally lightweight and text-oriented so it can be fed
    directly into the existing RAG + LLM stack, or into standalone generators.
    """

    def build_context(
        self,
        user_query: str,
        product_data: List[Dict[str, Any]],
        customer_profile: Dict[str, Any],
        retrieved_docs: List[Dict[str, Any]],
    ) -> str:
        """
        Assemble a rich, human-readable context string for retail tasks.

        The shape is compatible with the simpler specification provided in the
        hackathon brief but extended with a few extra labels so prompts can
        reason about where each piece came from.
        """
        context_parts: List[str] = []

        context_parts.append("USER QUERY:")
        context_parts.append(user_query)

        context_parts.append("\nCUSTOMER PROFILE:")
        context_parts.append(str(customer_profile or {}))

        context_parts.append("\nPRODUCT DATA:")
        for product in product_data or []:
            context_parts.append(str(product))

        context_parts.append("\nKNOWLEDGE BASE:")
        for doc in retrieved_docs or []:
            text = doc.get("text") or (doc.get("payload") or {}).get("text")
            if text:
                context_parts.append(str(text))

        return "\n".join(context_parts)


__all__ = ["RetailContextBuilder"]

