from __future__ import annotations

from typing import Any, Dict


class MultilingualResponseGenerator:
    """
    Simple template-based response generator for Swiss retail bundles.

    It formats a bundle-style message in the user's language using the
    structured solution produced by the shopper agent.
    """

    def __init__(self) -> None:
        self.templates: Dict[str, Dict[str, str]] = {
            "coop": {
                "de": "Verfügbar: {bundle} für {price:.2f} CHF. Abholung {location}.",
                "fr": "Disponible : {bundle} pour {price:.2f} CHF. Retrait {location}.",
                "it": "Disponibile: {bundle} per {price:.2f} CHF. Ritiro {location}.",
                "en": "Available: {bundle} for {price:.2f} CHF. Pickup at {location}.",
            },
            "migros": {
                "de": "Migros-Bundle: {bundle} für {price:.2f} CHF. Abholung {location}.",
                "fr": "Bundle Migros : {bundle} pour {price:.2f} CHF. Retrait {location}.",
                "it": "Bundle Migros: {bundle} per {price:.2f} CHF. Ritiro {location}.",
                "en": "Migros bundle: {bundle} for {price:.2f} CHF. Pickup at {location}.",
            },
        }

    def _get_template(self, tenant: str, lang: str) -> str:
        tenant_templates = self.templates.get(tenant, self.templates["coop"])
        return tenant_templates.get(lang, tenant_templates["de"])

    def generate_response(self, solution: Dict[str, Any], detected_lang: str, tenant: str) -> str:
        products = solution.get("products") or []
        if isinstance(products, str):
            bundle = products
        else:
            bundle = ", ".join(str(p) for p in products) if products else "keine Produkte"
        price = float(solution.get("total_chf") or 0.0)
        location = solution.get("pickup_location") or "online"

        template = self._get_template(tenant, detected_lang)
        return template.format(bundle=bundle, price=price, location=location)


__all__ = ["MultilingualResponseGenerator"]

