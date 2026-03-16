
""
Seed demo data: products (with text+image vectors), demo episodes and a sample goal.
Run: python scripts/ingest.py
"""
import logging
import os

from app.qdrant_client import get_qdrant_client
from app.qdrant_utils import upsert_points, upsert_named_vector_point
from app.embeddings import embed_texts, embed_image
from app.config import COLL_PRODUCTS, COLL_EPISODES, COLL_GOALS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_products(client) -> None:
    products = [
        {
            "sku": "TENT_221",
            "title": "Lightweight 2-person tent",
            "price": 179,
            "stock": True,
            "region": "Zurich",
            "image": "demo_data/tent_221.jpg",
        },
        {
            "sku": "TENT_322",
            "title": "Family tent 4-person",
            "price": 299,
            "stock": True,
            "region": "Zurich",
            "image": "demo_data/tent_322.jpg",
        },
    ]
    for product in products:
        text_vec = embed_texts([product["title"]])[0].tolist()
        image_vec = (
            embed_image(product["image"]).tolist()
            if os.path.exists(product["image"])
            else None
        )
        pid = f"product::{product['sku']}"
        payload = {k: v for k, v in product.items() if k != "image"}
        vectors = {"text_vector": text_vec}
        if image_vec is not None:
            vectors["image_vector"] = image_vec
        upsert_named_vector_point(client, COLL_PRODUCTS, pid, vectors, payload)
    logger.info("Seeded %s products.", len(products))


def seed_episodes_and_goals(client) -> None:
    episodes = [
        {
            "goal_id": "goal_demo_1",
            "solution_id": "sol_demo_1",
            "success": True,
            "summary": "2-person tent cheap, delivered 2 days",
            "region": "Zurich",
        }
    ]
    ids = []
    vectors = []
    payloads = []
    for idx, episode in enumerate(episodes):
        txt = f"{episode['summary']} region:{episode['region']}"
        vec = embed_texts([txt])[0].tolist()
        eid = f"episode::{idx}"
        ids.append(eid)
        vectors.append(vec)
        payloads.append(episode)
    upsert_points(client, COLL_EPISODES, vectors, payloads, ids)
    logger.info("Seeded %s episodes.", len(ids))

    goal_text = (
        "I need a 2-person tent under 200CHF deliver to Zurich by Friday"
    )
    goal_vec = embed_texts([goal_text])[0].tolist()
    upsert_points(
        client,
        COLL_GOALS,
        [goal_vec],
        [
            {
                "goal_text": goal_text,
                "status": "open",
                "region": "Zurich",
            }
        ],
        ["goal::demo1"],
    )
    logger.info("Seeded demo goal.")


if __name__ == "__main__":
    qdrant = get_qdrant_client()
    seed_products(qdrant)
    seed_episodes_and_goals(qdrant)
    logger.info("Ingest complete.")

