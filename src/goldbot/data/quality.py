"""Data quality helpers for cached price files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd

from goldbot.config import settings


def load_cached_prices(
    symbol: str = "XAUUSD",
    timeframe: str = "1h",
    provider: str = "twelvedata",
    fmt: str = "parquet",
) -> pd.DataFrame:
    """Load cached OHLCV data saved by the CLI."""

    filename = f"{symbol.lower().replace('/', '')}_{timeframe.lower()}_{provider}.{fmt}"
    path = settings.data.raw_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"Cached file not found: {path}")
    if fmt == "parquet":
        return pd.read_parquet(path)
    if fmt == "csv":
        return pd.read_csv(path, parse_dates=["datetime"]).set_index("datetime")
    raise ValueError(f"Unsupported format {fmt}")


@dataclass(slots=True)
class DataQualityReport:
    n_rows: int
    start: pd.Timestamp
    end: pd.Timestamp
    missing_rows: int
    missing_pct: float
    duplicate_rows: int
    timezone: str


def compute_quality_report(df: pd.DataFrame, freq: str = "1H") -> DataQualityReport:
    """Generate quick diagnostics (gaps, duplicates, coverage)."""

    df = df.sort_index()
    expected = pd.date_range(df.index.min(), df.index.max(), freq=freq, tz=df.index.tz)
    missing_idx = expected.difference(df.index)
    duplicate_rows = int(df.index.duplicated().sum())
    return DataQualityReport(
        n_rows=len(df),
        start=df.index.min(),
        end=df.index.max(),
        missing_rows=len(missing_idx),
        missing_pct=(len(missing_idx) / len(expected)) * 100 if expected.size else 0.0,
        duplicate_rows=duplicate_rows,
        timezone=str(df.index.tz),
    )

