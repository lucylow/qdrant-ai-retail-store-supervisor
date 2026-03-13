"""Create Qdrant price forecasting collections (price_history, forecast_accuracy, competitor_strategies)."""

from __future__ import annotations

import asyncio
import sys

from app.qdrant.forecasting.collections import setup_price_forecast_collections


def main() -> None:
    asyncio.run(setup_price_forecast_collections())
    print("Price forecasting collections OK.")


if __name__ == "__main__":
    main()
    sys.exit(0)
