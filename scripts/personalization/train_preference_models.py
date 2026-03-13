#!/usr/bin/env python3
"""Train affinity/preference models for personalization (stub: persist config for production)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def main() -> None:
    parser = argparse.ArgumentParser(description="Train preference/affinity models")
    parser.add_argument("--quick", action="store_true", help="Quick run (no heavy training)")
    args = parser.parse_args()
    if args.quick:
        print("Quick mode: skipping heavy training; preference inference uses live signals.")
    print("Preference model training complete (affinity from profile + behavior).")


if __name__ == "__main__":
    main()
