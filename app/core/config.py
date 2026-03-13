"""Pydantic Settings for env validation and type-safe configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class QdrantSettings(BaseSettings):
    """Qdrant connection and HNSW parameters."""

    model_config = SettingsConfigDict(env_prefix="QDRANT_", extra="ignore")

    url: str | None = None
    host: str = "localhost"
    port: int = Field(6333, ge=1, le=65535)
    api_key: str | None = None
    timeout: int = Field(60, ge=1, le=300)
    hnsw_m: int = Field(16, ge=4, le=64)
    hnsw_ef_construct: int = Field(200, ge=32, le=512)
    hnsw_ef_search: int = Field(128, ge=16, le=512)

    def connection_url(self) -> str:
        """Build connection URL for Qdrant client."""
        return self.url or f"http://{self.host}:{self.port}"


class CollectionSettings(BaseSettings):
    """Qdrant collection names (tenant-scoped via env)."""

    model_config = SettingsConfigDict(env_prefix="COLL_", extra="ignore")

    products: str = "products"
    goals: str = "goals"
    solutions: str = "solutions"
    episodes: str = "episodes"
    events: str = "events"
    messages: str = "messages"


class ModelSettings(BaseSettings):
    """Embedding and generator model names."""

    model_config = SettingsConfigDict(extra="ignore")

    text_embedding_model: str = "sentence-transformers/all-mpnet-base-v2"
    image_embedding_model: str = "clip-ViT-B-32"
    cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    generator_provider: str = "hf"
    generator_model: str = "meta-llama/Llama-2-13b-chat-hf"


class ContextSettings(BaseSettings):
    """RAG context and retrieval limits."""

    model_config = SettingsConfigDict(extra="ignore")

    max_total_tokens: int = Field(2048, ge=256, le=8192)
    max_context_documents: int = Field(8, ge=1, le=64)
    min_document_score: float = Field(0.05, ge=0.0, le=1.0)
    context_fingerprint_ttl_s: int = Field(3600, ge=60, le=86400)


class AppSettings(BaseSettings):
    """Root application settings (env validation)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    project_name: str = "multi_agent_store_supervisor_v5_hybrid_rag"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    base_dir: Path = Field(default_factory=lambda: Path("/tmp").resolve())
    artifacts_dir: Path | None = None

    qdrant: QdrantSettings = Field(default_factory=QdrantSettings)
    collections: CollectionSettings = Field(default_factory=CollectionSettings)
    models: ModelSettings = Field(default_factory=ModelSettings)
    context: ContextSettings = Field(default_factory=ContextSettings)


_settings: AppSettings | None = None


def get_settings() -> AppSettings:
    """Return singleton app settings (loads from env once)."""
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings
