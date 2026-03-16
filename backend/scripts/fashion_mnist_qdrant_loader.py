#!/usr/bin/env python3
"""
Fashion-MNIST → Qdrant visual search pipeline.
Loads 70K images (60K train + 10K test), encodes with CLIP (image + text),
creates collection "fashion_clip" with named vectors and rich payloads.
Run: python -m scripts.fashion_mnist_qdrant_loader
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import FASHION_CLIP_COLLECTION, MODELS
from app.qdrant_client import get_qdrant_client
from qdrant_client.http import models as qmodels

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FASHION_LABELS = [
    "T-shirt/top",
    "Trouser",
    "Pullover",
    "Dress",
    "Coat",
    "Sandal",
    "Shirt",
    "Sneaker",
    "Bag",
    "Ankle boot",
]
BATCH_SIZE = 1000
CLIP_DIM = 512


def load_fashion_mnist(data_dir: str = "data/fashion-mnist"):
    """Load Fashion-MNIST train + test (70K images)."""
    import torch
    from torchvision import datasets, transforms

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,)),
    ])
    train_set = datasets.FashionMNIST(
        data_dir, train=True, transform=transform, download=True
    )
    test_set = datasets.FashionMNIST(
        data_dir, train=False, transform=transform, download=True
    )
    return torch.utils.data.ConcatDataset([train_set, test_set])


def main() -> None:
    from sentence_transformers import SentenceTransformer
    from torchvision import transforms

    logger.info("Loading CLIP model: %s", MODELS.image_embedding_model)
    clip_model = SentenceTransformer(MODELS.image_embedding_model)

    logger.info("Loading Fashion-MNIST (70K images)...")
    dataset = load_fashion_mnist()
    total = len(dataset)

    client = get_qdrant_client()

    # Recreate collection with named vectors
    logger.info("Creating collection %s with image + text vectors (512d)", FASHION_CLIP_COLLECTION)
    client.recreate_collection(
        collection_name=FASHION_CLIP_COLLECTION,
        vectors_config=qmodels.VectorsConfig(
            named_vectors={
                "image": qmodels.NamedVectorParams(
                    size=CLIP_DIM, distance=qmodels.Distance.COSINE
                ),
                "text": qmodels.NamedVectorParams(
                    size=CLIP_DIM, distance=qmodels.Distance.COSINE
                ),
            }
        ),
    )

    points: list[qmodels.PointStruct] = []
    for idx in range(total):
        image, label = dataset[idx]
        # Tensor (C,H,W) → PIL for CLIP
        img_pil = transforms.ToPILImage()(image)
        image_embedding = clip_model.encode(img_pil, convert_to_numpy=True)
        if not isinstance(image_embedding, np.ndarray):
            image_embedding = np.array(image_embedding, dtype=np.float32)
        image_vec = image_embedding.flatten().tolist()

        text = f"{FASHION_LABELS[label]} fashion item"
        text_embedding = clip_model.encode(text, convert_to_numpy=True)
        if not isinstance(text_embedding, np.ndarray):
            text_embedding = np.array(text_embedding, dtype=np.float32)
        text_vec = text_embedding.flatten().tolist()

        payload = {
            "id": idx,
            "category": FASHION_LABELS[label],
            "label_id": int(label),
            "price": round(float(np.random.uniform(25, 250)), 2),
            "stock_status": np.random.choice(
                ["in_stock", "low_stock"], p=[0.85, 0.15]
            ),
            "color": np.random.choice(
                ["black", "white", "red", "blue", "gray"]
            ),
            "style": np.random.choice(["casual", "formal", "sporty"]),
        }

        points.append(
            qmodels.PointStruct(
                id=f"fmnist_{idx}",
                vector={"image": image_vec, "text": text_vec},
                payload=payload,
            )
        )

        if len(points) >= BATCH_SIZE or idx == total - 1:
            client.upsert(collection_name=FASHION_CLIP_COLLECTION, points=points)
            points = []
            logger.info("Indexed %s / %s images", idx + 1, total)

    logger.info("Done: 70K Fashion-MNIST images indexed in %s", FASHION_CLIP_COLLECTION)


if __name__ == "__main__":
    main()
