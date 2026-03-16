"""
Offline evaluation of retrieval-conditioned generation.
Input: queries.json -> [{"query":"", "gold_answer":"", "gold_docs":[doc_ids], "contexts":[...]}]
Outputs BLEU/ROUGE scores, grounding fraction (answers with >=1 citation linking to gold docs), and a small CSV for human eval.
"""
import csv
import json
from pathlib import Path
from typing import List, Dict, Any

from datasets import load_metric

from app.generation.generator import generate_answer


def dummy_retrieve(query: str, collection: str) -> List[Dict[str, Any]]:
    """
    Placeholder retriever for offline evaluation.
    Replace with real retrieval logic from your system (e.g., Qdrant search).
    """
    return []


def evaluate(queries_json: str, collection: str, out_csv: str = "eval_results.csv") -> None:
    queries = json.load(open(queries_json))
    rouge = load_metric("rouge")
    bleu = load_metric("bleu")
    rows = []

    preds = []
    refs = []

    for q in queries:
        retrieved = dummy_retrieve(q["query"], collection)
        gen = generate_answer(q["query"], retrieved)
        gold_answer = q.get("gold_answer") or ""
        if gold_answer:
            preds.append(gen["answer"])
            refs.append([gold_answer])
        # grounding: does any provenance id match gold_docs
        grounding = False
        for prov in gen.get("provenance", []):
            if prov.get("id") in (q.get("gold_docs") or []):
                grounding = True
        rows.append(
            {
                "query": q["query"],
                "gen": gen["answer"],
                "grounded": grounding,
                "confidence": gen.get("confidence"),
            }
        )

    if preds and refs:
        rouge_score = rouge.compute(predictions=preds, references=refs)
        bleu_score = bleu.compute(predictions=[p.split() for p in preds], references=[[r[0].split()] for r in refs])
        print("ROUGE:", rouge_score)
        print("BLEU:", bleu_score)

    # write csv for human eval
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(
            fh, fieldnames=["query", "gen", "grounded", "confidence"]
        )
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print("Wrote", out_csv)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("queries_json", help="Path to queries JSON file.")
    parser.add_argument("collection", help="Collection name.")
    parser.add_argument("--out-csv", default="eval_results.csv")
    args = parser.parse_args()
    evaluate(args.queries_json, args.collection, args.out_csv)

