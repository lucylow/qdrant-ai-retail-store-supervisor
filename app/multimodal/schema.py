"""
Named vector schema for Qdrant products collection (multimodal: text, image, audio, video).

Vector Name   | Source        | Dim  | Model           | Use Case
--------------|---------------|------|-----------------|------------------
textvector    | title+desc    | 1536 | bge-m3          | Semantic search
imagevector   | product photo | 512  | CLIP-ViT-B/32   | Visual similarity
audiovector   | 30s demo      | 384  | NVmix-8B        | Voice queries
videovector   | 10s clip      | 768  | VideoCLIP       | Motion/sequence
"""

from __future__ import annotations

from qdrant_client.http import models as qmodels

# Spec dimensions (hackathon: use sentence-transformers/CLIP where available, stubs for audio/video)
TEXT_DIM = 1536   # bge-m3; fallback all-MiniLM → 384, pad to 1536 or use separate config
IMAGE_DIM = 512   # CLIP-ViT-B/32
AUDIO_DIM = 384   # NVmix-8B or placeholder
VIDEO_DIM = 768   # VideoCLIP or average-pool CLIP frames + project

# Collection name for 4-vector product index (can coexist with single-vector "products")
PRODUCTS_MULTIMODAL_COLLECTION = "products_multimodal"


def get_products_multimodal_vectors_config() -> qmodels.VectorsConfig:
    """Return Qdrant VectorsConfig for products with 4 named vectors."""
    return qmodels.VectorsConfig(
        named_vectors={
            "textvector": qmodels.NamedVectorParams(size=TEXT_DIM, distance=qmodels.Distance.COSINE),
            "imagevector": qmodels.NamedVectorParams(size=IMAGE_DIM, distance=qmodels.Distance.COSINE),
            "audiovector": qmodels.NamedVectorParams(size=AUDIO_DIM, distance=qmodels.Distance.COSINE),
            "videovector": qmodels.NamedVectorParams(size=VIDEO_DIM, distance=qmodels.Distance.COSINE),
        }
    )
