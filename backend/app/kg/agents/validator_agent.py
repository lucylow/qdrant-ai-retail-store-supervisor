"""KG Validator Agent: entity resolution and relationship validation for ingest pipelines."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.kg.validator import (
    ValidationResult,
    validate_node,
    validate_relationship,
    resolve_entity_candidates,
)


class KGValidatorAgent:
    """
    Validates nodes and relationships before KG write.
    Used by ingest scripts to ensure schema compliance and entity resolution.
    """

    def __init__(self) -> None:
        pass

    def validate_node(self, node_type: str, properties: Dict[str, Any]) -> ValidationResult:
        """Validate a node against retail ontology."""
        return validate_node(node_type, properties)

    def validate_relationship(
        self,
        from_type: str,
        rel_type: str,
        to_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Validate relationship type and endpoints."""
        return validate_relationship(from_type, rel_type, to_type, properties)

    def resolve_entity(
        self,
        node_type: str,
        raw_id: str,
        candidates: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Resolve best-matching entity from candidates (entity resolution)."""
        return resolve_entity_candidates(node_type, raw_id, candidates)
