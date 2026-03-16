"""
Convert eval_results.csv into tasks for human evaluators.
Outputs CSV with columns: task_id, query, candidate_A, candidate_B, gold_answer, instructions
"""
import csv
import uuid
from pathlib import Path


def prepare_for_human_eval(eval_csv: str, out_csv: str = "human_eval_tasks.csv") -> None:
    rows = []
    with open(eval_csv, newline="", encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        for rec in r:
            task_id = str(uuid.uuid4())
            rows.append(
                {
                    "task_id": task_id,
                    "query": rec["query"],
                    "candidate_A": rec["gen"],
                    "candidate_B": "",  # If you have baseline, put it here
                    "gold_answer": "",
                    "instructions": "Choose which candidate is better: grounded, helpful, and concise.",
                }
            )
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(
            fh,
            fieldnames=[
                "task_id",
                "query",
                "candidate_A",
                "candidate_B",
                "gold_answer",
                "instructions",
            ],
        )
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print("Wrote", out_csv)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("eval_csv")
    parser.add_argument("--out-csv", default="human_eval_tasks.csv")
    args = parser.parse_args()
    prepare_for_human_eval(args.eval_csv, args.out_csv)

