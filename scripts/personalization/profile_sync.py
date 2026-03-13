#!/usr/bin/env python3
"""Real-time CDP profile sync: refresh Customer 360 in Qdrant from source systems."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.personalization.profile_builder import ProfileBuilderAgent


async def sync_one(customer_id: str, context: dict) -> None:
    builder = ProfileBuilderAgent()
    profile = await builder.build_profile(customer_id, context)
    await builder.qdrant.upsert_profile(customer_id, profile)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync Customer 360 profiles to Qdrant")
    parser.add_argument("--customer", type=str, help="Single customer ID to sync")
    parser.add_argument("--channel", type=str, default="web")
    args = parser.parse_args()
    if args.customer:
        asyncio.run(sync_one(args.customer, {"channel": args.channel}))
        print(f"Synced profile for {args.customer}")
    else:
        print("No --customer provided; run with --customer cust_123 to sync one profile.")


if __name__ == "__main__":
    main()
