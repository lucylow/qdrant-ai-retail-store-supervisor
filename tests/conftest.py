# Pytest configuration for GenAI and async tests (production fixtures)
from __future__ import annotations

import asyncio
from typing import Any, Generator
from unittest.mock import MagicMock

import pytest

from app.core.config import AppSettings, get_settings


def pytest_configure(config: Any) -> None:
    config.addinivalue_line("markers", "asyncio: mark test as async")
    config.addinivalue_line("markers", "integration: mark test as integration (e2e)")
    config.addinivalue_line("markers", "performance: mark test as performance (load)")


@pytest.fixture
def event_loop() -> asyncio.AbstractEventLoop:
    """Provide event loop for pytest-asyncio."""
    return asyncio.new_event_loop()


@pytest.fixture
def settings() -> AppSettings:
    """Production settings (from env or defaults)."""
    return get_settings()


@pytest.fixture
def qdrant_mock() -> Generator[MagicMock, None, None]:
    """Mock Qdrant client for unit tests."""
    client = MagicMock()
    client.get_collections.return_value = MagicMock(collections=[])
    client.retrieve.return_value = []
    client.scroll.return_value = ([], None)
    yield client


@pytest.fixture
def redis_mock() -> Generator[MagicMock, None, None]:
    """Mock Redis for cache unit tests."""
    store: dict[str, bytes] = {}

    def get(key: str) -> bytes | None:
        return store.get(key)

    def set(key: str, value: bytes, ex: int | None = None) -> bool:
        store[key] = value
        return True

    mock = MagicMock()
    mock.get = get
    mock.set = set
    yield mock
