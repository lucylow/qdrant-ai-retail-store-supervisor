"""Unit tests for app.utils.retry."""

from __future__ import annotations

import asyncio

import pytest

from app.utils.retry import retry_on_exception


@pytest.mark.asyncio
async def test_retry_succeeds_first_try() -> None:
    calls = 0

    @retry_on_exception(max_attempts=3, exceptions=(ValueError,))
    async def ok() -> str:
        nonlocal calls
        calls += 1
        return "ok"

    result = await ok()
    assert result == "ok"
    assert calls == 1


@pytest.mark.asyncio
async def test_retry_succeeds_second_try() -> None:
    calls = 0

    @retry_on_exception(max_attempts=3, backoff_factor=0.01, exceptions=(ValueError,))
    async def fail_once() -> str:
        nonlocal calls
        calls += 1
        if calls < 2:
            raise ValueError("transient")
        return "ok"

    result = await fail_once()
    assert result == "ok"
    assert calls == 2


@pytest.mark.asyncio
async def test_retry_raises_after_max_attempts() -> None:
    calls = 0

    @retry_on_exception(max_attempts=2, backoff_factor=0.01, exceptions=(ValueError,))
    async def always_fail() -> str:
        nonlocal calls
        calls += 1
        raise ValueError("fail")

    with pytest.raises(ValueError, match="fail"):
        await always_fail()
    assert calls == 2
