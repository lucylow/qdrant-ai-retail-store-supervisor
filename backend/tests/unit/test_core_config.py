"""Unit tests for app.core.config (Pydantic Settings)."""

from __future__ import annotations

import os

import pytest

from app.core.config import (
    AppSettings,
    CollectionSettings,
    ContextSettings,
    QdrantSettings,
    get_settings,
)


def test_get_settings_returns_app_settings() -> None:
    s = get_settings()
    assert isinstance(s, AppSettings)


def test_qdrant_connection_url_with_host_port() -> None:
    q = QdrantSettings(host="localhost", port=6333, url=None)
    assert q.connection_url() == "http://localhost:6333"


def test_qdrant_connection_url_prefers_url() -> None:
    q = QdrantSettings(url="https://cloud.qdrant.io", host="x", port=6333)
    assert q.connection_url() == "https://cloud.qdrant.io"


def test_collection_settings_defaults() -> None:
    c = CollectionSettings()
    assert c.products == "products"
    assert c.goals == "goals"


def test_context_settings_bounds() -> None:
    c = ContextSettings(max_total_tokens=1024, max_context_documents=8)
    assert 256 <= c.max_total_tokens <= 8192
    assert 1 <= c.max_context_documents <= 64
