"""
Multimodal RAG for video/audio: embed raw audio/video into Qdrant alongside text/images.

Named vectors: textvector (bge-m3), imagevector (CLIP), audiovector (NVmix), videovector (VideoCLIP).
Hybrid retrieval via RRF fusion for voice + photo + text queries.
"""

from app.multimodal.schema import (
    PRODUCTS_MULTIMODAL_COLLECTION,
    get_products_multimodal_vectors_config,
    TEXT_DIM,
    IMAGE_DIM,
    AUDIO_DIM,
    VIDEO_DIM,
)
from app.multimodal.search import multimodal_search, rrf_fusion
from app.multimodal.indexing import index_video_product, index_product_vectors

__all__ = [
    "PRODUCTS_MULTIMODAL_COLLECTION",
    "get_products_multimodal_vectors_config",
    "TEXT_DIM",
    "IMAGE_DIM",
    "AUDIO_DIM",
    "VIDEO_DIM",
    "multimodal_search",
    "rrf_fusion",
    "index_video_product",
    "index_product_vectors",
]
