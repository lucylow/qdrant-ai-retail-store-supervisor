from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from agents.retail_api_client import RetailAPIClient, RetailAPIConfig
from agents.swiss_supervisor_agent import SwissSupervisorAgent

router = APIRouter(prefix="/swiss", tags=["swiss-retail"])


def get_tenant_from_header(x_tenant_key: str) -> str:
    """
    Hackathon-simple tenant resolution from X-Tenant-Key header.

    In a fuller multi-tenant setup this should validate and map to
    a tenant id + plan.
    """
    if not x_tenant_key:
        raise HTTPException(status_code=400, detail="Missing X-Tenant-Key header")
    return x_tenant_key


def get_api_keys_for_tenant(tenant_id: str) -> Dict[str, str]:
    """
    Resolve retailer API keys for a tenant from environment variables.
    Mock-first: we only care about Coop and Migros keys for now.
    """
    import os

    return {
        "coop": os.getenv("COOP_LESHOP_API_KEY", ""),
        "migros": os.getenv("MIGROS_ONLINE_API_KEY", ""),
    }


def build_supervisor(tenant_id: str) -> SwissSupervisorAgent:
    api_keys = get_api_keys_for_tenant(tenant_id)
    config = RetailAPIConfig(tenant_id=tenant_id, api_keys=api_keys)
    client = RetailAPIClient(config)
    return SwissSupervisorAgent(client)


@router.post("/coop/leshop/dairy")
async def coop_dairy_bundle(
    query: str,
    region: str = "ZH",
    x_tenant_key: str = Depends(get_tenant_from_header),
) -> Dict[str, Any]:
    """
    Coop leShop.ch dairy bundle demo endpoint.
    """
    supervisor = build_supervisor(x_tenant_key)
    result = await supervisor.handle_swiss_query("coop", query, region)
    return result


@router.post("/migros/seasonal")
async def migros_seasonal_bundle(
    query: str,
    season: str = "winter",
    region: str = "ZH",
    x_tenant_key: str = Depends(get_tenant_from_header),
) -> Dict[str, Any]:
    """
    Migros Online seasonal bundles (fondue, ski gear).
    """
    supervisor = build_supervisor(x_tenant_key)
    # For now we delegate purely to merchandising; region reserved for later use.
    _ = region
    result = await supervisor.handle_swiss_query("migros", query, region="ZH")
    # Attach explicit season to response
    if result.get("merchandising_solution"):
        result["merchandising_solution"]["season"] = season
    return result

