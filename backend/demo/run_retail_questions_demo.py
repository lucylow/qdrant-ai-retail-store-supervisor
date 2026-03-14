"""
Demo: Agentic Retail Question Answering

This script showcases how the Agentic RAG stack answers core retail questions:
- Which products should we promote this week?
- What bundles increase average order value?
- Which inventory items are at risk of stockout?
- Generate marketing copy for our best-selling products.
- What promotion campaign should we run next month?
- Which products are best for cross-sell?
- Which items should be discounted?
- What products should we highlight on the homepage?
- What are the top-performing categories this season?
"""

from __future__ import annotations

from typing import List

from app.vector_store.retail_memory import RetailVectorMemory
from app.generative_ai import RetailContentGenerator
from app.assistant.retail_copilot import RetailCopilot
from app.assistant.retail_question_answerer import RetailQuestionAnswerer


def _seed_sample_products(memory: RetailVectorMemory) -> None:
    products = [
        {
            "id": "p_winter_jacket",
            "name": "ArcticShield Winter Jacket",
            "category": "outerwear",
            "description": "Warm waterproof winter jacket ideal for cold-season promotions.",
            "seasonality": ["winter"],
            "price": 199.0,
            "inventory_level": 40,
            "reorder_point": 30,
        },
        {
            "id": "p_thermal_gloves",
            "name": "Thermal Gloves",
            "category": "accessories",
            "description": "Insulated thermal gloves frequently bought with jackets.",
            "seasonality": ["winter"],
            "price": 29.0,
            "inventory_level": 150,
            "reorder_point": 50,
        },
        {
            "id": "p_rain_boots",
            "name": "StormGuard Rain Boots",
            "category": "footwear",
            "description": "Waterproof rain boots popular in shoulder seasons.",
            "seasonality": ["spring", "fall"],
            "price": 89.0,
            "inventory_level": 20,
            "reorder_point": 25,
        },
    ]
    memory.store_products_batch(products)


def main() -> None:
    memory = RetailVectorMemory()
    generator = RetailContentGenerator()
    copilot = RetailCopilot(vector_store=memory, generator=generator)
    qa = RetailQuestionAnswerer(copilot=copilot)

    _seed_sample_products(memory)

    questions: List[str] = [
        "Which products should we promote this week?",
        "What bundles increase average order value?",
        "Which inventory items are at risk of stockout?",
        "Generate marketing copy for our best-selling products.",
        "What promotion campaign should we run next month?",
        "Which products are best for cross-sell?",
        "Which items should be discounted?",
        "What products should we highlight on the homepage?",
        "What are the top-performing categories this season?",
    ]

    for q in questions:
        print("\n" + "=" * 80)
        print(f"QUESTION: {q}")
        result = qa.answer(q)
        print(f"\n[Agent Used] {result.agent_used}")
        print(f"[Type] {result.question_type}  |  [Confidence] {result.confidence:.2f}")
        print("\n--- ANSWER ---")
        print(result.answer_text)
        print("\n--- REASONING ---")
        print(result.reasoning)


if __name__ == "__main__":
    main()

