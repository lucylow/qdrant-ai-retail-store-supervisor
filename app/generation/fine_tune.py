"""
Helpers to prepare datasets and kick off fine-tuning for:
- cross-encoder reranker (sentence-transformers)
- seq2seq generator (transformers)
This file provides dataset conversion utilities and a simple Hugging Face Trainer example for seq2seq.
"""

import json
from typing import List, Dict, Any


def prepare_reranker_pairs(hard_negatives_json: str, out_tsv: str) -> None:
    """
    Input: hard_negatives_json = [{"query": "...", "positive": "...", "negative": "..."}]
    Output: tsv with columns: query \\t positive \\t negative (for pair/triples)
    """
    data = json.load(open(hard_negatives_json))
    with open(out_tsv, "w", encoding="utf-8") as fh:
        for item in data:
            q = item["query"].replace("\t", " ")
            pos = item["positive"].replace("\t", " ")
            neg = item["negative"].replace("\t", " ")
            fh.write(f"{q}\t{pos}\t{neg}\n")


def prepare_generator_dataset(pairs_json: str, out_jsonl: str) -> None:
    """
    Convert pairs of {question, contexts[], answer} into HF-compatible jsonl with input_text -> target_text.
    """
    data = json.load(open(pairs_json))
    with open(out_jsonl, "w", encoding="utf-8") as fh:
        for item in data:
            input_text = item.get("question") + "\n\n" + "\n".join(
                [f"[{i}] {c}" for i, c in enumerate(item.get("contexts", []))]
            )
            target_text = item.get("answer")
            fh.write(
                json.dumps({"input_text": input_text, "target_text": target_text}) + "\n"
            )

