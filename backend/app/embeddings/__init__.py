# Embeddings package: legacy API + high-performance batch/async/cache.
from app.embeddings.legacy import (
    EmbeddingResult,
    embed_texts,
    embed_single,
    get_text_embedding_dimension,
    normalize_rows,
    as_list,
    embed_image,
)
from app.embeddings.batch_embedder import BatchEmbedder
from app.embeddings.async_embedder import AsyncEmbedder
from app.embeddings.cache import EmbeddingCache
from app.embeddings.pooling import mean_pool, max_pool, truncate_sequences

__all__ = [
    "EmbeddingResult",
    "embed_texts",
    "embed_single",
    "get_text_embedding_dimension",
    "normalize_rows",
    "as_list",
    "embed_image",
    "BatchEmbedder",
    "AsyncEmbedder",
    "EmbeddingCache",
    "mean_pool",
    "max_pool",
    "truncate_sequences",
]
