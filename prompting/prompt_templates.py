from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class RetailPromptTemplate:
    """
    Simple prompt template with named slots and basic validation.
    """

    name: str
    template: str

    def format(self, **kwargs: Any) -> str:
        return self.template.format(**kwargs)


INVENTORY_INSIGHT_PROMPT = RetailPromptTemplate(
    name="inventory_insight",
    template=(
        "You are a senior retail planner.\n"
        "Question: {question}\n\n"
        "Context:\n{context}\n\n"
        "Using the context above, analyze inventory risk, "
        "highlight top issues, and propose concrete replenishment actions.\n"
        "Return a concise answer."
    ),
)


def validate_structured_inventory_output(data: Dict[str, Any]) -> bool:
    """
    Minimal schema validation for inventory insight outputs.
    Expected shape:
      {
        'high_risk_products': [ { 'name': str, 'stock': int, 'reorder_point': int } ],
        'summary': str
      }
    """
    if not isinstance(data, dict):
        return False
    if "high_risk_products" not in data or "summary" not in data:
        return False
    if not isinstance(data["high_risk_products"], list):
        return False
    for item in data["high_risk_products"]:
        if not isinstance(item, dict):
            return False
        if "name" not in item or "stock" not in item or "reorder_point" not in item:
            return False
    return True


def rank_documents_by_relevance(
    docs: List[Dict[str, Any]], key: str = "score"
) -> List[Dict[str, Any]]:
    """
    Utility for explicit document ranking based on a numeric score.
    Documents without the key are pushed to the end.
    """
    return sorted(
        docs,
        key=lambda d: (d.get(key) is not None, d.get(key)),
        reverse=True,
    )

