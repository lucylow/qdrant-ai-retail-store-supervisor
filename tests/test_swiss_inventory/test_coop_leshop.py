from __future__ import annotations

import numpy as np
import pytest

from .helpers import (
    audit_service,
    create_episode,
    full_agent_pipeline,
    inventory_agent,
    load_coop_dairy_episodes,
    shopper_agent,
    compute_stockout_rate,
    mock_customer_photo,
    mock_dress_image_embedding,
    mock_fondue_embedding,
    mock_milk_embedding,
)


@pytest.mark.parametrize(
    "query,expected_bundle",
    [
        (
            "Bio-milch laktosefrei 2L Zürich HB morgen abholen",
            {
                "products": [
                    "bio_milk_lactose_free_2L",
                    "muesli_oat_500g",
                    "yogurt_natural_500g",
                ],
                "total_chf": 12.95,
                "pickup_location": "ZH_HB",
                "eta": "tomorrow_10-12",
                "stockout_risk": 0.12,
            },
        ),
        (
            "Fondue Käse + Brot für 4 Personen Genf Wochenende",
            {
                "products": ["kaese_fondue_2kg", "brot_rund_1kg_x2"],
                "total_chf": 45.80,
                "delivery": "GE_weekend",
                "waste_risk": 0.08,
            },
        ),
    ],
)
def test_coop_perishable_bundles(query: str, expected_bundle: dict) -> None:
    """Coop dairy/perishable bundle optimisation with stockout + waste KPIs."""
    result = inventory_agent.optimize_bundle(
        tenant_id="coop",
        query=query,
        region="ZH",
        max_budget=20,
    )
    product_ids = [p["id"] for p in result["products"]]

    assert product_ids == expected_bundle["products"]
    assert result["total_chf"] <= expected_bundle["total_chf"] * 1.05  # 5% tolerance
    # Coop pickup/delivery fields should match scenario
    if "pickup_location" in expected_bundle:
        assert result["pickup_location"] == expected_bundle["pickup_location"]
    if "delivery" in expected_bundle:
        assert result["delivery"] == expected_bundle["delivery"]


def test_coop_stockout_reduction() -> None:
    """67% stockout reduction via joint inventory-pricing narrative."""
    baseline_stockouts = 18  # % from business doc
    episodes = load_coop_dairy_episodes()
    post_agent_stockouts = compute_stockout_rate(episodes)
    assert post_agent_stockouts <= baseline_stockouts * 0.33  # 67% reduction


@pytest.mark.parametrize(
    "season_query,expected",
    [
        (
            "Fondue set für 4, Käse + Topf, Genf Wochenende",
            {
                "products": ["kaese_fondue_2kg", "fondue_pot_4person", "white_wine_750ml"],
                "season_boost": True,
                "margin_uplift": 0.184,
            },
        ),
        (
            "Ski goggles + gloves + base layer, St. Moritz pickup",
            {
                "products": ["ski_goggles_mirrored", "ski_gloves_black", "base_layer_merino"],
                "region_penalty": 0.15,
                "pickup": "st_moritz",
            },
        ),
    ],
)
def test_migros_seasonal_bundles(season_query: str, expected: dict) -> None:
    """Migros seasonal peaks: fondue (Nov–Feb), ski gear (Dec–Apr)."""
    result = inventory_agent.optimize_bundle(
        tenant_id="migros",
        query=season_query,
        date="2026-12-15",
    )
    product_ids = [p["id"] for p in result["products"]]
    for pid in expected["products"]:
        assert pid in product_ids

    if "season_boost" in expected:
        assert bool(result.get("season_boost", False)) is True
        assert result["margin_uplift"] >= expected["margin_uplift"]
    if "region_penalty" in expected:
        assert result["region_penalty"] <= expected["region_penalty"]


def test_denner_hyperlocal_staples() -> None:
    """Denner: ultra-thin margins, near-zero stockouts on staples."""
    query = "Brot + Milch für Familie 4, lokale Denner pickup"
    result = inventory_agent.optimize_bundle(
        tenant_id="denner",
        query=query,
        max_price=8.0,
    )
    product_ids = {p["id"] for p in result["products"]}
    assert "white_bread_500g" in product_ids
    assert "milk_1L_standard" in product_ids
    assert result["total_chf"] <= 8.0
    assert result["stockout_risk"] < 0.05


def test_manor_outfit_bundles() -> None:
    """Fashion: cross-category outfit coordination with visual context."""
    query = "Office outfit Frau Größe 38, Zürich Lieferung"
    result = inventory_agent.optimize_bundle(
        tenant_id="manor",
        query=query,
        image_embedding=mock_dress_image_embedding(),
    )
    product_ids = set(p["id"] for p in result["products"])
    expected_outfit = {"blouse_white_38", "skirt_black_38", "pumps_nude"}
    assert len(product_ids & expected_outfit) >= 2
    assert result["visual_similarity_score"] > 0.85


def test_zalando_visual_rag() -> None:
    """Zalando: 'dresses like this photo' + matching shoes under 150 CHF."""
    result = inventory_agent.visual_search(
        tenant_id="zalando",
        image_embedding=mock_customer_photo(),
        text_query="matching shoes under 150 CHF",
    )
    assert len(result["products"]) >= 3
    assert result["avg_visual_score"] > 0.90
    assert all(p["price_chf"] <= 150 for p in result["products"])


@pytest.mark.parametrize(
    "gift_query,expected_margin",
    [
        ("Läderach Schokolade Geschenk 6 Personen corporate Basel morgen", 0.65),
        ("Victorinox Messer + Reisetasche + Multi-Tool, Genf Flughafen pickup", 0.58),
    ],
)
def test_premium_gifting_bundles(gift_query: str, expected_margin: float) -> None:
    """Premium: high AOV, tourist urgency, airport pickup feasibility."""
    tenant = "laderach" if "Läderach" in gift_query else "victorinox"
    result = inventory_agent.optimize_bundle(
        tenant_id=tenant,
        query=gift_query,
        urgency="high",
    )
    assert result["margin_percent"] >= expected_margin
    assert result.get("airport_pickup_feasible", False)


def test_galaxus_tech_bundles() -> None:
    """Electronics: laptop + accessories, competitor price matching."""
    query = "Laptop + Tasche + Maus unter 1200 CHF"
    competitor_prices = {"amazon": 1150, "digitec": 1180}
    result = inventory_agent.optimize_bundle(
        tenant_id="galaxus",
        query=query,
        competitor_prices=competitor_prices,
    )
    product_ids = [p["id"] for p in result["products"]]
    assert result["total_chf"] <= 1180
    assert "laptop_i5_16gb" in product_ids
    accessory_count = sum(1 for p in result["products"] if p.get("category") == "accessory")
    assert accessory_count >= 2


@pytest.mark.parametrize(
    "region,expected_penalty",
    [
        ("St. Moritz", 0.15),
        ("Zermatt", 0.20),
        ("Genf Flughafen", 0.05),
        ("Zürich HB", 0.00),
    ],
)
def test_alpine_delivery_penalties(region: str, expected_penalty: float) -> None:
    """Alpine logistics: higher penalties for remote regions and ski gear."""
    result = inventory_agent.compute_eta_feasibility(
        tenant_id="migros",
        region=region,
        product_category="ski_gear",
    )
    assert abs(result["delivery_penalty"] - expected_penalty) < 0.02


@pytest.mark.parametrize(
    "lang_query,expected_lang",
    [
        ("Bio-milch laktosefrei Zürich", "DE"),
        ("Lait bio sans lactose Genève", "FR"),
        ("Latte biologico senza lattosio Zurigo", "IT"),
        ("Organic milk lactose-free Zurich", "EN"),
    ],
)
def test_multilingual_query_processing(lang_query: str, expected_lang: str) -> None:
    """Multilingual: DE/FR/IT/EN shopper intent parsing."""
    result = shopper_agent.parse_intent(lang_query)
    assert result["detected_language"] == expected_lang
    assert result["structured_goal"]["category"] == "dairy"


def test_tenant_isolation_coop_vs_migros() -> None:
    """Coop episodes invisible to Migros and vice versa."""
    create_episode(tenant_id="coop", products=["bio_milk"])
    create_episode(tenant_id="migros", products=["fondue_kit"])

    coop_retrieval = inventory_agent.search_similar(
        tenant_id="coop",
        query_embedding=mock_milk_embedding(),
    )
    coop_product_ids = {p["id"] for p in coop_retrieval["products"]}
    assert "fondue_kit" not in coop_product_ids

    migros_retrieval = inventory_agent.search_similar(
        tenant_id="migros",
        query_embedding=mock_fondue_embedding(),
    )
    migros_product_ids = {p["id"] for p in migros_retrieval["products"]}
    assert "bio_milk" not in migros_product_ids


def test_gdpr_anonymization() -> None:
    """No raw PII in payloads after anonymisation."""
    episode_with_pii = {
        "user_name": "Hans Müller",
        "phone": "+41 79 123 45 67",
        "products": ["milk"],
    }
    anonymized = audit_service.anonymize_episode(episode_with_pii)
    assert "user_name" not in anonymized
    assert "phone" not in anonymized
    assert anonymized.get("user_pseudo_id") is not None


def test_coop_leshop_pilot_demo() -> None:
    """End-to-end Coop leShop.ch demo flow KPIs."""
    query = "Bio-milch laktosefrei 2L Zürich HB morgen"
    result = full_agent_pipeline(
        tenant_id="coop",
        query=query,
        profile="leshop_grocery",
    )
    assert result["conversion_lift_estimate"] >= 0.23
    assert result["stockout_reduction"] >= 0.67
    assert result["total_value_created_chf"] >= 9_500_000
    assert result["subscription_roi"] >= 79

