"""Command-line helpers for data tasks."""

from __future__ import annotations

import argparse

from goldbot.config import settings
from goldbot.data import TwelveDataClient, save_price_data
from goldbot.utils.logging import configure_logging


def pull_prices() -> None:
    parser = argparse.ArgumentParser(description="Fetch and cache XAU/USD prices from Twelve Data")
    parser.add_argument("--symbol", default=settings.providers.default_symbol)
    parser.add_argument("--interval", default=settings.providers.default_interval)
    parser.add_argument("--outputsize", type=int, default=settings.providers.outputsize)
    parser.add_argument("--format", choices=["parquet", "csv"], default="parquet")
    args = parser.parse_args()

    configure_logging()
    client = TwelveDataClient()
    df = client.fetch_time_series(symbol=args.symbol, interval=args.interval, outputsize=args.outputsize)
    path = save_price_data(
        df=df,
        symbol=args.symbol,
        timeframe=args.interval,
        provider="twelvedata",
        fmt=args.format,
    )
    print(f"Saved {len(df)} rows to {path}")


if __name__ == "__main__":
    pull_prices()

