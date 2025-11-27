"""Data ingestion utilities for price series and macro context."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd
from loguru import logger

from goldbot.config import settings


@dataclass(slots=True)
class PriceDataLoader:
    """High-level interface for fetching XAUUSD data from CSV or API."""

    symbol: str = "XAUUSD"
    timeframe: str = "1H"
    source: str = "csv"  # csv | api
    path: Optional[Path] = None

    def load(self) -> pd.DataFrame:
        """Return price dataframe indexed by datetime."""

        if self.source == "csv":
            return self._load_from_csv()
        if self.source == "api":
            raise NotImplementedError("API loader not wired yet.")
        raise ValueError(f"Unknown source {self.source}")

    def _load_from_csv(self) -> pd.DataFrame:
        """Load OHLCV data from CSV located in data/raw."""

        csv_path = self.path or settings.data.raw_dir / f"{self.symbol}_{self.timeframe}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Missing price file: {csv_path}")

        df = pd.read_csv(csv_path, parse_dates=["timestamp"])
        df = df.set_index("timestamp").sort_index()
        expected_cols = {"open", "high", "low", "close", "volume"}
        missing = expected_cols - set(df.columns.str.lower())
        if missing:
            raise ValueError(f"CSV missing columns: {missing}")
        df.columns = df.columns.str.lower()
        return df


def resample_bars(df: pd.DataFrame, rule: str, ohlc_cols: Optional[list[str]] = None) -> pd.DataFrame:
    """Resample OHLCV dataframe to a different timeframe."""

    if df.empty:
        return df

    ohlc_cols = ohlc_cols or ["open", "high", "low", "close"]
    ohlc_dict = {col: "first" for col in ohlc_cols}
    ohlc_dict["high"] = "max"
    ohlc_dict["low"] = "min"
    ohlc_dict["close"] = "last"
    agg = df.resample(rule).agg({**ohlc_dict, "volume": "sum"})
    return agg.dropna(how="any")


def save_price_data(
    df: pd.DataFrame,
    symbol: str,
    timeframe: str,
    provider: str = "twelvedata",
    fmt: str = "parquet",
) -> Path:
    """Persist dataframe to canonical path in data/raw."""

    sanitized_symbol = symbol.lower().replace("/", "")
    filename = f"{sanitized_symbol}_{timeframe.lower()}_{provider}.{fmt}"
    target = settings.data.raw_dir / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "parquet":
        df.to_parquet(target)
    elif fmt == "csv":
        df.reset_index().to_csv(target, index=False)
    else:
        raise ValueError(f"Unsupported format {fmt}")
    logger.info("Saved %s rows to %s", len(df), target)
    return target

