from typing import Any, Dict

from app.llm_client import generate


class RetailContentGenerator:
    """
    Retail product content generator.

    This wraps the existing LLM client and follows the structure described
    in the hackathon spec, while remaining lightweight enough to run in
    constrained environments.
    """

    def __init__(self) -> None:
        # All configuration (model, provider, etc.) is handled by app.llm_client.
        pass

    def generate_product_description(self, context: str) -> str:
        """
        Generate rich product marketing copy from a plain-text context string.

        The prompt format mirrors the original example and asks the model
        to return a single coherent text block.
        """
        prompt = f"""
You are a retail marketing expert.

Using the context below generate:

1. Product Title
2. Product Description
3. 5 Bullet Points
4. SEO Keywords
5. Short Marketing Tagline

Return a well-formatted markdown block that clearly separates these sections.

Context:
{context}
"""

        return generate(prompt, max_tokens=400)

    def generate_content_bundle(self, context: str) -> Dict[str, Any]:
        """
        Higher-level helper that asks the model for a JSON-like bundle and
        attempts to parse it into a structured dict.
        """
        prompt = f"""
You are a senior retail copywriter.

Using the context below, generate a JSON object with the following keys:
- title: short product title
- description: 2-3 sentence description
- bullet_points: list of 5 concise bullets
- seo_keywords: list of keywords
- ad_copy: short ad headline + subline
- email_variant: short email subject + preview text

Return ONLY a JSON object, no extra text.

Context:
{context}
"""
        raw = generate(prompt, max_tokens=512)

        # Best-effort JSON parsing with graceful fallback; we do not want
        # brittle demo behavior if the model returns near-JSON.
        import json

        try:
            # Try direct parse first.
            return json.loads(raw)
        except json.JSONDecodeError:
            # Fallback: try to locate a JSON block.
            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(raw[start : end + 1])
                except json.JSONDecodeError:
                    pass

        return {"raw_text": raw}


__all__ = ["RetailContentGenerator"]

