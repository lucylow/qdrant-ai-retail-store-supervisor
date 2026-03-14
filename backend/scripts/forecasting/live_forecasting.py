"""Real-time price predictions: run forecasting for a SKU and optionally record accuracy."""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from app.forecasting.price.supervisor import PriceForecastSupervisor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    p = argparse.ArgumentParser(description="Live price forecasting")
    p.add_argument("--sku", default="tshirt_blue_m", help="SKU to forecast")
    p.add_argument("--store", default="store_001")
    p.add_argument("--horizon", type=int, default=30)
    args = p.parse_args()
    asyncio.run(_run(args.sku, args.store, args.horizon))


async def _run(sku: str, store_id: str, horizon: int) -> None:
    supervisor = PriceForecastSupervisor()
    forecast = await supervisor.forecast_price(sku, store_id, horizon)
    logger.info(
        "Forecast sku=%s horizon=%d action=%s accuracy=%.2f%% anomaly=%.2f%%",
        sku, horizon, forecast.recommended_action,
        (1 - forecast.accuracy_score) * 100, forecast.anomaly_probability * 100,
    )
    print(f"Point forecast mean: {forecast.point_forecast.mean():.2f}")
    print(f"Recommended action: {forecast.recommended_action}")


if __name__ == "__main__":
    main()
    sys.exit(0)
