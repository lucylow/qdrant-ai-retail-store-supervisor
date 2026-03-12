from app.context_manager import (
    build_profile,
    rewrite_query,
    fingerprint_context,
    compress_document_text,
)


def test_profile_building():
    p = build_profile(
        {"user": {"region": "Zurich"}, "product": {"title": "2-person tent"}}
    )
    assert p["region"] == "Zurich"
    assert p["product"]["title"] == "2-person tent"


def test_rewrite_query_basic():
    p = {
        "product": {"title": "2-person tent"},
        "task": {"intent": "buy for camping"},
    }
    q = rewrite_query(p, "cheap tent", expansion=False)
    assert "cheap" in q
    assert "2-person" in q or "2-person tent" in q


def test_fingerprint_consistent():
    f1 = fingerprint_context(["a", "b", "c"])
    f2 = fingerprint_context(["a", "b", "c"])
    assert f1 == f2


def test_compress_document_short():
    s = " ".join(["word"] * 500)
    c = compress_document_text(s, target_tokens=50)
    assert len(c) < len(s)

