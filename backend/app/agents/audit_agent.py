import logging
from typing import Dict, Any, List

from app.agents.interfaces import safe_execute, timed
from app.agents.safety import validate_solution_against_policies
from app.generator import rag_answer

logger = logging.getLogger(__name__)


class AuditAgent:
    name = "AuditAgent"

    @safe_execute
    @timed
    def run(self, context: Dict[str, Any]):
        solutions: List[Dict[str, Any]] = (
            context.get("candidate_solutions")
            or context.get("solutions")
            or []
        )
        if not solutions:
            return {"status": "skipped", "reason": "no solutions to audit"}

        policy = context.get("policy", {})
        user = context.get("user", {})

        results = []
        for s in solutions:
            ok, reasons = validate_solution_against_policies(s)

            # Use RAG to generate a short, grounded audit explanation.
            question = (
                f"Audit this solution for policy compliance and customer impact: {s}"
            )
            context_input: Dict[str, Any] = {
                "user": user,
                "agent": {"name": "AuditAgent"},
                "task": {"intent": "policy and safety audit"},
                "product": {},
                "collection": context.get("collection", "products"),
                "policy": policy,
            }
            rag = rag_answer(context_input, question, token_budget=512)

            results.append(
                {
                    "solution_id": s.get("bundle_id") or s.get("id"),
                    "ok": ok,
                    "reasons": reasons,
                    "rag_explanation": rag.get("answer"),
                    "rag_provenance": rag.get("provenance"),
                }
            )
        return {"audit_results": results}

