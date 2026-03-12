import json
import argparse
import statistics

from app.context_manager import build_context_for_query
from app.generator import rag_answer


def evaluate(queries_file: str, collection: str = "products") -> None:
    queries = json.load(open(queries_file))
    results = []

    for q in queries:
        profile_in = {
            "user": q.get("user", {}),
            "agent": {"name": "eval"},
            "collection": collection,
        }
        ctx = build_context_for_query(profile_in, q["query"])
        out = rag_answer(profile_in, q["query"])

        prov_ids = [p.get("id") for p in out.get("provenance", [])]
        gold_docs = q.get("gold_docs") or []
        grounded = any(pid in gold_docs for pid in prov_ids)

        results.append(
            {
                "query": q["query"],
                "grounded": grounded,
                "num_contexts": ctx["metadata"]["num_contexts"],
                "tokens_est": ctx["metadata"]["tokens_used_est"],
            }
        )

    grounded_frac = (
        sum(1 for r in results if r["grounded"]) / len(results) if results else 0.0
    )
    print("Grounded fraction:", grounded_frac)
    print(
        "Avg contexts:",
        statistics.mean([r["num_contexts"] for r in results]) if results else 0,
    )
    print(
        "Avg tokens:",
        statistics.mean([r["tokens_est"] for r in results]) if results else 0,
    )

    with open("context_eval_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Wrote context_eval_results.json")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("queries_json")
    p.add_argument("--collection", default="products")
    args = p.parse_args()
    evaluate(args.queries_json, args.collection)

