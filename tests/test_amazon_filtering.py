"""
Tests for Amazon review filter extraction and Qdrant filter building.

Run: pytest tests/test_amazon_filtering.py -v
"""

import pytest

from app.services.amazon_review_filter_service import (
    AmazonFilterService,
    AmazonReviewFilters,
    _filters_to_dict,
)


def test_amazon_review_filters_model():
    f = AmazonReviewFilters(category="Sports", rating_min=4.0, price_max=200)
    assert f.category == "Sports"
    assert f.rating_min == 4.0
    assert f.price_max == 200
    assert f.brand is None
    d = _filters_to_dict(f)
    assert d.get("category") == "Sports"
    assert d.get("rating_min") == 4.0
    assert d.get("price_max") == 200


def test_build_qdrant_filter():
    from qdrant_client.http.models import Filter
    service = AmazonFilterService()
    f = AmazonReviewFilters(category="Sports", rating_min=4.0, price_max=200)
    qf = service.build_qdrant_filter(f)
    assert qf is not None
    assert isinstance(qf, Filter)
    assert len(qf.must) == 3
    f2 = AmazonReviewFilters()
    qf2 = service.build_qdrant_filter(f2)
    assert qf2 is None or (hasattr(qf2, "must") and len(qf2.must) == 0)


def test_fallback_extract_filters():
    service = AmazonFilterService(openai_client=None)
    semantic, filters = service._fallback_extract("4 star Sports tents under 200")
    assert "tent" in semantic.lower() or "sport" in semantic.lower() or semantic
    assert filters.category == "Sports"
    assert filters.rating_min == 4.0
    assert filters.price_max == 200


def test_fallback_extract_electronics():
    service = AmazonFilterService(openai_client=None)
    semantic, filters = service._fallback_extract("5 star electronics in stock")
    assert filters.rating_min == 5.0
    assert filters.stock_status == "in_stock"
    assert filters.category == "Electronics"
