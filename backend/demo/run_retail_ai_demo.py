"""
Hackathon-friendly demo script for the AI Retail Store Supervisor pieces.

This script wires together:
- RetailVectorMemory (Qdrant + embeddings)
- RetailContentGenerator (LLM wrapper)
- RetailCopilot (high-level assistant)

and runs a single end-to-end marketing-style query.
"""

from __future__ import annotations

from typing import Any, Dict, List

from app.vector_store.retail_memory import RetailVectorMemory
from app.generative_ai import RetailContentGenerator
from app.assistant import RetailCopilot


def _seed_sample_products(memory: RetailVectorMemory) -> None:
    """
    Seed a few in-memory products into Qdrant so the demo works out of the box.
    """
    products: List[Dict[str, Any]] = [
        {
            "id": "p_winter_jacket_1",
            "name": "ArcticShield Winter Jacket",
            "category": "outerwear",
            "brand": "Northwind",
            "description": (
                "Premium insulated winter jacket with waterproof shell, "
                "fleece-lined hood, and windproof zippers. Ideal for cold "
                "urban commutes and snowy weekend getaways."
            ),
            "seasonality": ["winter", "holiday"],
            "price": 199.0,
            "currency": "USD",
            "inventory_level": 120,
        },
        {
            "id": "p_winter_jacket_2",
            "name": "Summit Pro Down Parka",
            "category": "outerwear",
            "brand": "SummitLine",
            "description": (
                "Lightweight down parka with 700-fill insulation, storm cuffs, "
                "and reflective details. Designed for active customers who want "
                "warmth without bulk."
            ),
            "seasonality": ["winter"],
            "price": 249.0,
            "currency": "USD",
            "inventory_level": 80,
        },
    ]
    memory.store_products_batch(products)


def main() -> None:
    memory = RetailVectorMemory()
    generator = RetailContentGenerator()
    copilot = RetailCopilot(vector_store=memory, generator=generator)

    _seed_sample_products(memory)

    question = "Generate product marketing for winter jackets"
    print(f"QUESTION: {question}\n")
    response = copilot.answer(question)
    print("=== RETAIL COPILOT RESPONSE ===")
    print(response)


if __name__ == "__main__":
    main()

