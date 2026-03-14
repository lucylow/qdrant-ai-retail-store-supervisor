from __future__ import annotations

from typing import List, Sequence

from app.agents.inventory import Product
from app.rag.multimodal import MultimodalRAG


class DummyImageGenerator:
    """
    Stand-in for Stable Diffusion / FLUX style model.
    """

    def generate(self, prompt: str, condition_on: List[str]) -> str:
        return f"mock://image?prompt={prompt[:64]}&n_refs={len(condition_on)}"


class MultimodalProductGenerator:
    """
    Generation pipeline combining multimodal RAG with an image generator.
    """

    def __init__(
        self,
        rag: MultimodalRAG | None = None,
        image_gen: DummyImageGenerator | None = None,
    ) -> None:
        self.rag = rag or MultimodalRAG()
        self.image_gen = image_gen or DummyImageGenerator()

    def generate_bundle_mockup(
        self,
        products: List[Product],
        customer_avatar: str | None = None,
    ) -> str:
        # CLIP multimodal retrieval → top-3 bundle images
        retrieved_images = self.rag.multimodal_retrieve(products)

        # Stable Diffusion/FLUX conditioned on retrieved assets
        prompt = f"Photorealistic bundle: {[p.name for p in products]} on white background"
        if customer_avatar:
            prompt += f", styled for customer: {customer_avatar}"

        mockup = self.image_gen.generate(prompt, condition_on=retrieved_images)
        return mockup


__all__: Sequence[str] = ["MultimodalProductGenerator", "DummyImageGenerator"]

