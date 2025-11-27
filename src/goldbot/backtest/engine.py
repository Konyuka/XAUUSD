"""Lightweight vectorized backtesting harness."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from goldbot.config import settings


@dataclass(slots=True)
class BacktestResult:
    equity_curve: pd.Series
    trades: pd.DataFrame
    stats: dict[str, float]


class VectorizedBacktester:
    def __init__(self, initial_capital: float | None = None) -> None:
        self.initial_capital = initial_capital or settings.backtest.initial_capital

    def run(self, signals: pd.DataFrame) -> BacktestResult:
        df = signals.copy()
        df["returns"] = df["close"].pct_change().fillna(0)
        df["strategy_ret"] = df["position"].shift(1).fillna(0) * df["returns"]
        df["strategy_ret"] -= settings.backtest.commission_perc * df["returns"].abs()

        equity = (1 + df["strategy_ret"]).cumprod() * self.initial_capital
        trades = self._extract_trades(df)
        stats = self._compute_stats(df["strategy_ret"], equity)
        return BacktestResult(equity_curve=equity, trades=trades, stats=stats)

    @staticmethod
    def _compute_stats(returns: pd.Series, equity: pd.Series) -> dict[str, float]:
        cagr = (equity.iloc[-1] / equity.iloc[0]) ** (252 / len(equity)) - 1
        vol = returns.std() * np.sqrt(252)
        sharpe = (returns.mean() * 252 - settings.backtest.risk_free_rate) / (vol or 1e-9)
        drawdown = (equity / equity.cummax()) - 1
        max_dd = drawdown.min()
        return {
            "cagr": float(cagr),
            "volatility": float(vol),
            "sharpe": float(sharpe),
            "max_drawdown": float(max_dd),
        }

    @staticmethod
    def _extract_trades(df: pd.DataFrame) -> pd.DataFrame:
        positions = df["position"].fillna(0)
        entries = (positions.diff() != 0).astype(int)
        trades = df.loc[entries == 1, ["close", "position"]].copy()
        trades.rename(columns={"close": "entry_price"}, inplace=True)
        return trades

