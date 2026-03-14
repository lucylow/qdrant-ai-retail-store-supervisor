"""
Cultural configuration for Swiss retailers (Coop, Migros, Denner, Läderach, etc.).
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, List

from pydantic import BaseModel


class SwissLanguage(Enum):
    DE = "de"
    FR = "fr"
    IT = "it"
    EN = "en"
    RM = "rm"  # Romansh (rare)


class SwissCanton(Enum):
    ZH = "Zürich"
    GE = "Genève"
    BS = "Basel"
    TI = "Ticino"
    GR = "Graubünden"  # Alpine


class RetailerCulture(BaseModel):
    name: str
    primary_languages: List[SwissLanguage]
    cooperative_culture: bool = False  # Coop/Migros = True
    sustainability_focus: float = 0.5  # 0.0-1.0 priority
    pickup_preferences: Dict[str, float] = {}  # Canton -> preference
    seasonal_events: List[str] = []

    # Cultural pricing sensitivity
    price_sensitive: bool = False  # Denner
    premium_focus: bool = False  # Läderach


SWISS_RETAILERS: Dict[str, RetailerCulture] = {
    "coop": RetailerCulture(
        name="Coop",
        primary_languages=[SwissLanguage.DE, SwissLanguage.FR],
        cooperative_culture=True,
        sustainability_focus=0.9,
        pickup_preferences={"ZH": 0.4, "GE": 0.3, "BS": 0.2},
        seasonal_events=["fondue_nov_feb", "easter_chocolate"],
    ),
    "migros": RetailerCulture(
        name="Migros",
        primary_languages=[SwissLanguage.DE, SwissLanguage.FR, SwissLanguage.IT],
        cooperative_culture=True,
        sustainability_focus=0.85,
        pickup_preferences={"ZH": 0.35, "GE": 0.25, "TI": 0.15},
        seasonal_events=["ski_dec_apr", "fondue_nov_feb", "summer_bbq"],
    ),
    "denner": RetailerCulture(
        name="Denner",
        primary_languages=[SwissLanguage.DE],
        cooperative_culture=False,
        price_sensitive=True,
        sustainability_focus=0.6,
        pickup_preferences={},
        seasonal_events=[],
    ),
    "laderach": RetailerCulture(
        name="Läderach",
        primary_languages=[SwissLanguage.DE, SwissLanguage.EN],
        premium_focus=True,
        sustainability_focus=0.95,
        pickup_preferences={},
        seasonal_events=[],
    ),
}
