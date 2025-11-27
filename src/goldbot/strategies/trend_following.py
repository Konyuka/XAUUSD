"""Baseline trend-following strategy using moving averages."""

from __future__ import annotations

import pandas as pd

from goldbot.strategies.base import BaseStrategy


class DualMovingAverageStrategy(BaseStrategy):
    name = "dual_ma_trend"

    def __init__(self, fast: int = 21, slow: int = 55) -> None:
        self.fast = fast
        self.slow = slow

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df[f"sma_{self.fast}"] = df["close"].rolling(self.fast).mean()
        df[f"sma_{self.slow}"] = df["close"].rolling(self.slow).mean()
        df["signal"] = 0
        df.loc[df[f"sma_{self.fast}"] > df[f"sma_{self.slow}"], "signal"] = 1
        df.loc[df[f"sma_{self.fast}"] < df[f"sma_{self.slow}"], "signal"] = -1
        df["position"] = df["signal"].shift(1).fillna(0)
        return df

