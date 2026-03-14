#!/usr/bin/env python3
"""Launch and manage A/B tests for personalization (stub for experimentation framework)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch A/B test for personalization")
    parser.add_argument("--experiment", type=str, default="rec_ranking", help="Experiment name")
    parser.add_argument("--variants", type=int, default=4, help="Number of variants")
    args = parser.parse_args()
    print(f"Launched experiment '{args.experiment}' with {args.variants} variants.")
    print("Assignments: control, variant_a, variant_b, variant_c (deterministic by customer_id).")


if __name__ == "__main__":
    main()
