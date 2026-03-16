"""
Build Discovery API context tables from RetailRocket events.

Reads events.parquet (or events.csv) and writes discovery_co_viewed.parquet,
discovery_co_carted.parquet, discovery_co_purchased.parquet for use by
app.services.retailrocket_discovery.RetailRocketDiscovery.

Run after process_retailrocket.py (so events.parquet exists).

Usage:
  python data/retailrocket/build_discovery_contexts.py --data-dir data/retailrocket
  python data/retailrocket/build_discovery_contexts.py --data-dir data/retailrocket --max-events 500000
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.retailrocket_discovery import build_discovery_contexts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=str, default="data/retailrocket")
    parser.add_argument("--max-events", type=int, default=None)
    args = parser.parse_args()
    data_dir = Path(args.data_dir)
    events_path = data_dir / "events.parquet"
    if not events_path.exists():
        events_path = data_dir / "events.csv"
    if not events_path.exists():
        print("events.parquet or events.csv not found in --data-dir", file=sys.stderr)
        sys.exit(1)
    build_discovery_contexts(events_path, data_dir, max_events=args.max_events)
    print("Discovery contexts ready.")


if __name__ == "__main__":
    main()
