# Pytest configuration for GenAI and async tests
import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as async")

# pytest-asyncio: run async tests with asyncio
@pytest.fixture
def event_loop():
    import asyncio
    return asyncio.new_event_loop()
