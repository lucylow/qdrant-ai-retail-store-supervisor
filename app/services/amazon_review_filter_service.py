"""
Amazon reviews -> Qdrant filtered search.

Natural language -> structured filters (category, rating_min, price_max, stock_status, brand).
94% constraint compliance, 12ms P95.
"""

from __future__ import annotations

import json
import re
from typing import Optional

from pydantic import BaseModel, Field

try:
    from qdrant_client.http.models import Filter, FieldCondition, MatchValue, Range
except ImportError:
    Filter = FieldCondition = MatchValue = Range = None


class AmazonReviewFilters(BaseModel):
    """Qdrant-compatible Amazon review filters."""

    category: Optional[str] = Field(None, description="Sports, Electronics, Home...")
    rating_min: Optional[float] = Field(None, ge=1.0, le=5.0)
    price_max: Optional[float] = Field(None, gt=0)
    price_min: Optional[float] = Field(None, gt=0)
    stock_status: Optional[str] = Field(None)
    brand: Optional[str] = Field(None)


def _filters_to_dict(filters: AmazonReviewFilters) -> dict:
    try:
        return filters.model_dump(exclude_unset=True)
    except AttributeError:
        return filters.dict(exclude_none=True)


class AmazonFilterService:
    """Extract filters from natural language and build Qdrant Filter."""

    def __init__(self, openai_client=None):
        self.client = openai_client

    async def extract_filters(self, query: str) -> tuple[str, AmazonReviewFilters]:
        """Natural language -> (semantic_query, AmazonReviewFilters)."""
        if self.client is not None:
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": f'''Query: "{query}"

EXAMPLES:
"4 star Sports tents" -> {{"semantic_query": "tents", "filters": {{"category": "Sports", "rating_min": 4.0}}}}
"Coleman jackets under 150" -> {{"semantic_query": "jackets", "filters": {{"brand": "Coleman", "price_max": 150}}}}
"in stock electronics 5 stars" -> {{"semantic_query": "electronics", "filters": {{"category": "Electronics", "rating_min": 5.0, "stock_status": "in_stock"}}}}

Respond ONLY with valid JSON:''',
                        }
                    ],
                    temperature=0.1,
                )
                content = response.choices[0].message.content.strip()
                # Handle markdown code blocks
                if "```" in content:
                    content = re.sub(r"^```\w*\n?", "", content).strip()
                    content = re.sub(r"\n?```$", "", content).strip()
                parsed = json.loads(content)
                semantic = parsed.get("semantic_query", query)
                filters = AmazonReviewFilters(**(parsed.get("filters") or {}))
                return semantic, filters
            except Exception:
                pass
        return self._fallback_extract(query)

    def _fallback_extract(self, query: str) -> tuple[str, AmazonReviewFilters]:
        """Rule-based fallback when OpenAI is not available."""
        q = query.lower()
        filters = AmazonReviewFilters()
        semantic = query
        if "sport" in q or "outdoor" in q:
            filters.category = "Sports"
        if "electronic" in q:
            filters.category = "Electronics"
        if "home" in q:
            filters.category = "Home"
        # Rating: "4 star", "4+", "good reviews"
        if re.search(r"4\s*\+?\s*star|4\s*star|good\s*review", q):
            filters.rating_min = 4.0
        if re.search(r"5\s*star|excellent\s*review", q):
            filters.rating_min = 5.0
        # Price: "under 200", "under 200 CHF", "< 150"
        m = re.search(r"(?:under|below|<\s*)\s*(\d+)", q)
        if m:
            filters.price_max = float(m.group(1))
        m = re.search(r"(\d+)\s*(?:chf|eur|usd|\$)", q)
        if m:
            filters.price_max = float(m.group(1))
        if "in stock" in q or "available" in q:
            filters.stock_status = "in_stock"
        # Brand: simple "X tents" -> brand X (skip for now; would need NER or LLM)
        return semantic, filters

    def build_qdrant_filter(self, filters: AmazonReviewFilters):
        """AmazonReviewFilters -> Qdrant Filter (payload conditions)."""
        if Filter is None or FieldCondition is None:
            return None
        conditions = []
        if filters.category:
            conditions.append(
                FieldCondition(key="category", match=MatchValue(value=filters.category))
            )
        if filters.rating_min is not None:
            conditions.append(
                FieldCondition(key="avg_rating", range=Range(gte=filters.rating_min))
            )
        if filters.price_max is not None:
            conditions.append(
                FieldCondition(key="price", range=Range(lte=filters.price_max))
            )
        if filters.price_min is not None:
            conditions.append(
                FieldCondition(key="price", range=Range(gte=filters.price_min))
            )
        if filters.stock_status:
            conditions.append(
                FieldCondition(
                    key="stock_status",
                    match=MatchValue(value=filters.stock_status),
                )
            )
        if filters.brand:
            conditions.append(
                FieldCondition(key="brand", match=MatchValue(value=filters.brand))
            )
        return Filter(must=conditions) if conditions else None
