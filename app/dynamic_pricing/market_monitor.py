"""Market monitor agent: competitor scraping + price indexing to Qdrant."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict

from app.data.pricing.competitor_prices import upsert_competitor_price

logger = logging.getLogger(__name__)


class _BaseScraper:
    """Base stub for competitor scrapers (replace with real scraping in production)."""

    async def get_price(self, sku: str) -> float:
        # Demo: deterministic from SKU hash
        return 30.0 + (hash(sku) % 15)


class AmazonScraper(_BaseScraper):
    async def get_price(self, sku: str) -> float:
        return 32.0 + (hash(sku) % 10) * 0.5


class Competitor1Scraper(_BaseScraper):
    async def get_price(self, sku: str) -> float:
        return 28.0 + (hash(sku) % 12) * 0.6


class Competitor2Scraper(_BaseScraper):
    async def get_price(self, sku: str) -> float:
        return 35.0 + (hash(sku) % 8) * 0.4


class MarketMonitorAgent:
    """Real-time competitor price monitoring and Qdrant indexing."""

    def __init__(self, qdrant_client: Any = None):
        self._qdrant = qdrant_client
        self.competitor_scrapers: Dict[str, _BaseScraper] = {
            "amazon": AmazonScraper(),
            "competitor_1": Competitor1Scraper(),
            "competitor_2": Competitor2Scraper(),
        }

    async def update_competitor_prices(self, sku: str, store_id: str = "global") -> Dict[str, float]:
        """Scrape competitor prices and upsert to Qdrant for RAG."""
        competitor_prices: Dict[str, float] = {}

        for platform, scraper in self.competitor_scrapers.items():
            try:
                price = await scraper.get_price(sku)
                competitor_prices[platform] = price
                upsert_competitor_price(sku=sku, platform=platform, price=price, store_id=store_id)
            except Exception as e:
                logger.warning("Failed to scrape %s for %s: %s", platform, sku, e)

        return competitor_prices
