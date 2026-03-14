from typing import List, Dict, Any
import textwrap


def build_image_prompt(
    product_payload: Dict[str, Any],
    retrieved_brand_assets: List[Dict[str, Any]],
    style_hint: str = "sleek tech retail display",
) -> str:
    """
    Build an image generation prompt that conditions on: product details + brand assets (colors, logos) + style hint.
    """
    lines = []
    lines.append(f"Product: {product_payload.get('title')}")
    lines.append(f"SKU: {product_payload.get('sku')}")
    lines.append(f"Key features: {product_payload.get('features', '')}")
    if retrieved_brand_assets:
        colors = [
            a.get("payload", {}).get("color_palette")
            for a in retrieved_brand_assets
            if a.get("payload")
        ]
        lines.append(f"Brand colors: {', '.join([c for c in colors if c][:3])}")
    lines.append(f"Style hint: {style_hint}")
    prompt = " | ".join(lines)
    # optional: more elaborate instruction
    final = textwrap.dedent(
        f"""
        Create a photorealistic store display image based on the following:
        {prompt}
        Focus on product visibility, modern digital displays, and consistent brand colors. No text overlays except subtle price tag.
        """
    )
    return final

