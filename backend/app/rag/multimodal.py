from __future__ import annotations

from typing import List, Sequence

from app.agents.inventory import Product


class MultimodalRAG:
    """
    Placeholder multimodal retrieval using product metadata.
    """

    def multimodal_retrieve(self, products: List[Product]) -> List[str]:
        # AUTONOMOUS-AGENT-HACKATHON: stub URLs for bundle mockups.
        return [f"https://example.invalid/images/{p.sku}.png" for p in products[:3]]


__all__: Sequence[str] = ["MultimodalRAG"]

