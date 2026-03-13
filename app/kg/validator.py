"""Entity resolution and KG schema/relationship validation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from app.kg.ontologies.retail import RETAIL_ONTOLOGY


@dataclass
class ValidationResult:
    """Result of validating an entity or relationship."""

    valid: bool
    errors: List[str]
    normalized: Optional[Dict[str, Any]] = None


def _normalize_id(value: Any, node_type: str) -> Optional[str]:
    """Normalize node id for entity resolution."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    # Lowercase for case-insensitive uniqueness where appropriate
    if node_type in ("Customer", "Product", "Supplier", "Warehouse", "Campaign", "Segment"):
        return s
    if node_type in ("Category", "Attribute", "Event", "Season"):
        return s.lower()
    return s


def validate_node(node_type: str, properties: Dict[str, Any]) -> ValidationResult:
    """
    Validate a node against the retail ontology.
    Returns normalized properties and any errors.
    """
    errors: List[str] = []
    if node_type not in RETAIL_ONTOLOGY["nodes"]:
        return ValidationResult(valid=False, errors=[f"Unknown node type: {node_type}"])

    meta = RETAIL_ONTOLOGY["nodes"][node_type]
    required_props = [meta.get("id_prop", "id")]
    allowed = set(meta.get("properties", []))

    normalized: Dict[str, Any] = {}
    for k, v in properties.items():
        if k not in allowed and allowed:
            errors.append(f"Unexpected property: {k}")
            continue
        if v is None or v == "":
            continue
        normalized[k] = v

    for req in required_props:
        if req not in normalized or normalized[req] is None:
            errors.append(f"Missing required property: {req}")
        else:
            normalized[req] = _normalize_id(normalized[req], node_type)

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        normalized=normalized if normalized else None,
    )


def validate_relationship(
    from_type: str,
    rel_type: str,
    to_type: str,
    properties: Optional[Dict[str, Any]] = None,
) -> ValidationResult:
    """Validate a relationship type and endpoint labels against ontology."""
    errors: List[str] = []
    rels = RETAIL_ONTOLOGY["relationships"]
    found = False
    for (f, r, t, props) in rels:
        if f == from_type and r == rel_type and t == to_type:
            found = True
            break
    if not found:
        errors.append(f"Unknown relationship: ({from_type})-[{rel_type}]->({to_type})")

    normalized = dict(properties or {})
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        normalized=normalized if normalized else None,
    )


def resolve_entity_candidates(
    node_type: str,
    raw_id: str,
    candidates: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    Entity resolution: pick best match from candidates for raw_id.
    Uses exact match first, then normalized match.
    """
    norm = _normalize_id(raw_id, node_type)
    for c in candidates:
        cid = c.get("id") or c.get("name") or ""
        if str(cid) == str(raw_id) or _normalize_id(cid, node_type) == norm:
            return c
    return None


__all__ = ["ValidationResult", "validate_node", "validate_relationship", "resolve_entity_candidates"]
