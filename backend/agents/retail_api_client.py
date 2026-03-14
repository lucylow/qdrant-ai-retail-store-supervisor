from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class Retailer(str, Enum):
    COOP = "coop"
    MIGROS = "migros"
    DENNER = "denner"
    MANOR = "manor"
    ZALANDO = "zalando"
    GALAXUS = "galaxus"


class RetailAPIConfig(BaseModel):
    """Per-tenant API configuration (mock-first, real URLs later)."""

    tenant_id: str
    api_keys: Dict[str, str]
    timeout_seconds: float = 5.0


class RetailAPIClient:
    """
    Unified async HTTP client for Swiss retailer APIs.

    Mock-first: base URLs currently point at placeholder endpoints.
    Real Coop/Migros/etc. URLs can be swapped in via configuration later.
    """

    def __init__(
        self,
        config: RetailAPIConfig,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.config = config
        self.base_urls: Dict[Retailer, str] = {
            Retailer.COOP: "https://api.leshop.ch/v2",
            Retailer.MIGROS: "https://api.migros.ch/online",
            Retailer.DENNER: "https://api.denner.ch/v1",
            Retailer.MANOR: "https://api.manor.ch/ecom",
            Retailer.ZALANDO: "https://api.zalando.ch/partners",
            Retailer.GALAXUS: "https://api.galaxus.ch/v1",
        }
        self._client = client or httpx.AsyncClient(timeout=self.config.timeout_seconds)

    async def close(self) -> None:
        await self._client.aclose()

    def _headers_for(self, retailer: Retailer) -> Dict[str, str]:
        api_key = self.config.api_keys.get(retailer.value, "")
        headers: Dict[str, str] = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    async def get_products(self, retailer: Retailer, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Real-time product catalog + stock from retailer API.

        For Coop/Migros this is typically category + region filtered.
        """
        url = f"{self.base_urls[retailer]}/products"
        params: Dict[str, Any] = {
            "category": filters.get("category"),
            "stock_status": filters.get("stock_status", "in_stock"),
            "region": filters.get("region", "ZH"),
            "tenant": self.config.tenant_id,
        }
        headers = self._headers_for(retailer)

        logger.debug("RetailAPIClient.get_products retailer=%s params=%s", retailer, params)
        resp = await self._client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        products = data.get("products") or data
        if not isinstance(products, list):
            logger.warning("Unexpected products payload shape: %s", type(products))
            return []
        return products

    async def get_inventory(self, retailer: Retailer, skus: List[str], region: str) -> Dict[str, Dict[str, Any]]:
        """
        Real-time stock levels by SKU + region.

        Returns mapping sku → {qty, eta, ...}.
        """
        url = f"{self.base_urls[retailer]}/inventory"
        payload: Dict[str, Any] = {"skus": skus, "region": region, "tenant": self.config.tenant_id}
        headers = self._headers_for(retailer)

        logger.debug("RetailAPIClient.get_inventory retailer=%s payload=%s", retailer, payload)
        resp = await self._client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        stock = data.get("stock") or data
        if not isinstance(stock, dict):
            logger.warning("Unexpected stock payload shape: %s", type(stock))
            return {}
        return stock

    async def get_pricing(self, retailer: Retailer, skus: List[str]) -> Dict[str, float]:
        """
        Dynamic pricing from retailer pricing engine.

        Returns mapping sku → price_chf.
        """
        url = f"{self.base_urls[retailer]}/pricing/dynamic"
        payload: Dict[str, Any] = {"skus": skus, "tenant": self.config.tenant_id}
        headers = self._headers_for(retailer)

        logger.debug("RetailAPIClient.get_pricing retailer=%s payload=%s", retailer, payload)
        resp = await self._client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        prices = data.get("prices") or data
        if not isinstance(prices, dict):
            logger.warning("Unexpected prices payload shape: %s", type(prices))
            return {}
        # ensure float values
        out: Dict[str, float] = {}
        for sku, price in prices.items():
            try:
                out[sku] = float(price)
            except Exception:  # noqa: BLE001
                logger.warning("Could not cast price for sku=%s value=%r", sku, price)
        return out


__all__ = ["RetailAPIClient", "RetailAPIConfig", "Retailer"]

