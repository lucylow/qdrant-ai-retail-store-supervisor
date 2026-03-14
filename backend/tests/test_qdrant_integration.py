from app.qdrant_client import get_qdrant_client, qdrant_health_check


def test_qdrant_client_connects() -> None:
    client = get_qdrant_client()
    assert client is not None


def test_health() -> None:
    client = get_qdrant_client()
    assert qdrant_health_check(client) is True

