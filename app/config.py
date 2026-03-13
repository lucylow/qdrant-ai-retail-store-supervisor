from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final, Optional

import os


PROJECT_NAME: Final[str] = "multi_agent_store_supervisor_v5_hybrid_rag"
LOG_LEVEL: Final[str] = os.getenv("LOG_LEVEL", "INFO")


@dataclass(frozen=True)
class QdrantSettings:
    url: Optional[str]
    host: str
    port: int
    api_key: Optional[str]
    hnsw_m: int
    hnsw_ef_construct: int
    hnsw_ef_search: int


@dataclass(frozen=True)
class ModelSettings:
    text_embedding_model: str
    image_embedding_model: str
    cross_encoder_model: str
    generator_provider: str
    generator_model: str


@dataclass(frozen=True)
class CollectionSettings:
    products: str
    goals: str
    solutions: str
    episodes: str
    events: str
    messages: str


@dataclass(frozen=True)
class ContextSettings:
    max_total_tokens: int
    max_context_documents: int
    min_document_score: float
    dense_summary_model: str
    context_fingerprint_ttl_s: int
    query_expansion_model: str
    hard_negative_margin: float
    provenance_weight: float


@dataclass(frozen=True)
class Neo4jSettings:
    uri: str
    user: str
    password: str
    max_connection_pool_size: int


@dataclass(frozen=True)
class FeatureToggles:
    enable_multimodal: bool
    enable_reranker: bool
    self_improve: bool


BASE_DIR: Final[Path] = Path(os.getenv("BASE_DIR", "/tmp")).resolve()
ARTIFACTS_DIR: Final[Path] = Path(
    os.getenv("ARTIFACTS_DIR", str(BASE_DIR / "artifacts"))
).resolve()

QDRANT: Final[QdrantSettings] = QdrantSettings(
    url=os.getenv("QDRANT_URL"),
    host=os.getenv("QDRANT_HOST", "localhost"),
    port=int(os.getenv("QDRANT_PORT", "6333")),
    api_key=os.getenv("QDRANT_API_KEY"),
    hnsw_m=int(os.getenv("HNSW_M", "16")),
    hnsw_ef_construct=int(os.getenv("HNSW_EF_CONSTRUCT", "200")),
    hnsw_ef_search=int(os.getenv("HNSW_EF_SEARCH", "128")),
)

MODELS: Final[ModelSettings] = ModelSettings(
    text_embedding_model=os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2"
    ),
    image_embedding_model=os.getenv("IMAGE_EMBEDDING_MODEL", "clip-ViT-B-32"),
    cross_encoder_model=os.getenv(
        "CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ),
    generator_provider=os.getenv("GENERATOR_PROVIDER", "hf"),
    generator_model=os.getenv(
        "GENERATOR_MODEL", "meta-llama/Llama-2-13b-chat-hf"
    ),
)

COLLECTIONS: Final[CollectionSettings] = CollectionSettings(
    products=os.getenv("COLL_PRODUCTS", "products"),
    goals=os.getenv("COLL_GOALS", "goals"),
    solutions=os.getenv("COLL_SOLUTIONS", "solutions"),
    episodes=os.getenv("COLL_EPISODES", "episodes"),
    events=os.getenv("COLL_EVENTS", "events"),
    messages=os.getenv("COLL_MESSAGES", "messages"),
)

CONTEXT: Final[ContextSettings] = ContextSettings(
    max_total_tokens=int(os.getenv("CONTEXT_MAX_TOTAL_TOKENS", "2048")),
    max_context_documents=int(os.getenv("MAX_CONTEXT_DOCS", "8")),
    min_document_score=float(os.getenv("MIN_DOCUMENT_SCORE", "0.05")),
    dense_summary_model=os.getenv(
        "DENSE_SUMMARY_MODEL", "facebook/bart-large-cnn"
    ),
    context_fingerprint_ttl_s=int(os.getenv("CONTEXT_FINGERPRINT_TTL", "3600")),
    query_expansion_model=os.getenv(
        "QUERY_EXPANSION_MODEL", "all-mpnet-base-v2"
    ),
    hard_negative_margin=float(os.getenv("HARD_NEGATIVE_MARGIN", "0.25")),
    provenance_weight=float(os.getenv("PROVENANCE_WEIGHT", "1.2")),
)

NEO4J: Final[Neo4jSettings] = Neo4jSettings(
    uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    user=os.getenv("NEO4J_USER", "neo4j"),
    password=os.getenv("NEO4J_PASSWORD", "password"),
    max_connection_pool_size=int(os.getenv("NEO4J_MAX_POOL_SIZE", "50")),
)

FEATURES: Final[FeatureToggles] = FeatureToggles(
    enable_multimodal=os.getenv("ENABLE_MULTIMODAL", "true").lower()
    in ("1", "true", "yes"),
    enable_reranker=os.getenv("ENABLE_RERANKER", "true").lower()
    in ("1", "true", "yes"),
    self_improve=os.getenv("SELF_IMPROVE", "true").lower() in ("1", "true", "yes"),
)

# LLM client compatibility (used by app.llm_client)
GENERATOR_PROVIDER: Final[str] = MODELS.generator_provider
GENERATOR_MODEL: Final[str] = MODELS.generator_model
GENERATOR_MAX_TOKENS: Final[int] = int(os.getenv("GENERATOR_MAX_TOKENS", "512"))
GENERATOR_TEMPERATURE: Final[float] = float(os.getenv("GENERATOR_TEMPERATURE", "0.2"))
GENERATOR_TOP_P: Final[float] = float(os.getenv("GENERATOR_TOP_P", "1.0"))


__all__ = [
    "PROJECT_NAME",
    "LOG_LEVEL",
    "BASE_DIR",
    "ARTIFACTS_DIR",
    "QDRANT",
    "NEO4J",
    "MODELS",
    "COLLECTIONS",
    "CONTEXT",
    "FEATURES",
    "GENERATOR_PROVIDER",
    "GENERATOR_MODEL",
    "GENERATOR_MAX_TOKENS",
    "GENERATOR_TEMPERATURE",
    "GENERATOR_TOP_P",
]
