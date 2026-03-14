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
    timeout: int
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


@dataclass(frozen=True)
class ExternalProviderSettings:
    """Production external APIs: HF, Whisper, Replicate, Groq (agent), ElevenLabs (TTS)."""

    hf_token: Optional[str]
    hf_text_model: str
    hf_image_model: str
    openai_api_key: Optional[str]
    replicate_api_token: Optional[str]
    use_external_embeddings: bool
    # LLM agent: Groq (42ms) or OpenAI GPT-4o mini for inventory/shopper reply
    groq_api_key: Optional[str]
    agent_provider: str  # "groq" | "openai" | "none"
    # TTS: German voice response (e.g. ElevenLabs)
    elevenlabs_api_key: Optional[str]
    elevenlabs_voice_id: str


EXTERNAL_PROVIDERS: Final[ExternalProviderSettings] = ExternalProviderSettings(
    hf_token=os.getenv("HF_TOKEN"),
    hf_text_model=os.getenv("HF_TEXT_MODEL", "BAAI/bge-m3"),
    hf_image_model=os.getenv("HF_IMAGE_MODEL", "openai/clip-vit-base-patch32"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    replicate_api_token=os.getenv("REPLICATE_API_TOKEN"),
    use_external_embeddings=os.getenv("USE_EXTERNAL_EMBEDDINGS", "false").lower()
    in ("1", "true", "yes"),
    groq_api_key=os.getenv("GROQ_API_KEY"),
    agent_provider=os.getenv("AGENT_PROVIDER", "groq").lower(),
    elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY"),
    elevenlabs_voice_id=os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL"),
)


BASE_DIR: Final[Path] = Path(os.getenv("BASE_DIR", "/tmp")).resolve()
ARTIFACTS_DIR: Final[Path] = Path(
    os.getenv("ARTIFACTS_DIR", str(BASE_DIR / "artifacts"))
).resolve()

QDRANT: Final[QdrantSettings] = QdrantSettings(
    url=os.getenv("QDRANT_URL"),
    host=os.getenv("QDRANT_HOST", "localhost"),
    port=int(os.getenv("QDRANT_PORT", "6333")),
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=int(os.getenv("QDRANT_TIMEOUT", "60")),
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

# Fashion-MNIST visual search (70K CLIP-embedded images)
FASHION_CLIP_COLLECTION: Final[str] = os.getenv("FASHION_CLIP_COLLECTION", "fashion_clip")

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


@dataclass(frozen=True)
class GenAISettings:
    """GENAI-HACKATHON: Production-grade GenAI engineering config."""

    max_retries: int
    cot_steps: int
    hallucination_block_threshold: float
    semantic_drift_max: float
    prompt_cache_ttl_s: int
    few_shot_k: int
    lexical_weight: float
    entailment_weight: float
    confidence_weight: float
    temporal_weight: float


GENAI: Final[GenAISettings] = GenAISettings(
    max_retries=int(os.getenv("GENAI_MAX_RETRIES", "3")),
    cot_steps=int(os.getenv("GENAI_COT_STEPS", "4")),
    hallucination_block_threshold=float(
        os.getenv("GENAI_HALLUCINATION_THRESHOLD", "0.25")
    ),
    semantic_drift_max=float(os.getenv("GENAI_SEMANTIC_DRIFT_MAX", "0.15")),
    prompt_cache_ttl_s=int(os.getenv("GENAI_PROMPT_CACHE_TTL", "3600")),
    few_shot_k=int(os.getenv("GENAI_FEW_SHOT_K", "3")),
    lexical_weight=float(os.getenv("GENAI_LEXICAL_WEIGHT", "0.4")),
    entailment_weight=float(os.getenv("GENAI_ENTAILMENT_WEIGHT", "0.4")),
    confidence_weight=float(os.getenv("GENAI_CONFIDENCE_WEIGHT", "0.1")),
    temporal_weight=float(os.getenv("GENAI_TEMPORAL_WEIGHT", "0.1")),
)

# LLM client compatibility (used by app.llm_client)
GENERATOR_PROVIDER: Final[str] = MODELS.generator_provider
GENERATOR_MODEL: Final[str] = MODELS.generator_model
GENERATOR_MAX_TOKENS: Final[int] = int(os.getenv("GENERATOR_MAX_TOKENS", "512"))
GENERATOR_TEMPERATURE: Final[float] = float(os.getenv("GENERATOR_TEMPERATURE", "0.2"))
GENERATOR_TOP_P: Final[float] = float(os.getenv("GENERATOR_TOP_P", "1.0"))

# Stripe (Swiss CHF, SCA/3DS, Apple Pay / Google Pay)
STRIPE_SECRET_KEY: Final[Optional[str]] = os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_SECRET")
STRIPE_WEBHOOK_SECRET: Final[Optional[str]] = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_PUBLISHABLE_KEY: Final[Optional[str]] = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_STATEMENT_DESCRIPTOR: Final[str] = os.getenv("STRIPE_STATEMENT_DESCRIPTOR", "Coop leShop CH")
STRIPE_COUNTRY: Final[str] = os.getenv("STRIPE_COUNTRY", "CH")

# ---------------------------------------------------------------------------
# Apertus-70B-2509 LLM configuration
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ApertusSettings:
    """swiss-ai/Apertus-70B-2509 — primary multilingual LLM backbone."""
    model: str
    backend: str  # local | remote | hf
    endpoint: str
    max_tokens: int
    temperature: float
    top_p: float


APERTUS: Final[ApertusSettings] = ApertusSettings(
    model=os.getenv("APERTUS_MODEL", "swiss-ai/Apertus-70B-2509"),
    backend=os.getenv("APERTUS_BACKEND", "remote").lower(),
    endpoint=os.getenv("APERTUS_ENDPOINT", "http://localhost:8000/v1"),
    max_tokens=int(os.getenv("APERTUS_MAX_TOKENS", "1024")),
    temperature=float(os.getenv("APERTUS_TEMPERATURE", "0.3")),
    top_p=float(os.getenv("APERTUS_TOP_P", "0.95")),
)

__all__ = [
    "PROJECT_NAME",
    "LOG_LEVEL",
    "BASE_DIR",
    "ARTIFACTS_DIR",
    "QDRANT",
    "NEO4J",
    "MODELS",
    "COLLECTIONS",
    "FASHION_CLIP_COLLECTION",
    "CONTEXT",
    "FEATURES",
    "EXTERNAL_PROVIDERS",
    "ExternalProviderSettings",
    "GENAI",
    "GenAISettings",
    "GENERATOR_PROVIDER",
    "GENERATOR_MODEL",
    "GENERATOR_MAX_TOKENS",
    "GENERATOR_TEMPERATURE",
    "GENERATOR_TOP_P",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "STRIPE_PUBLISHABLE_KEY",
    "STRIPE_STATEMENT_DESCRIPTOR",
    "STRIPE_COUNTRY",
    "APERTUS",
    "ApertusSettings",
]
