"""Strategy interfaces and reusable helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd


class Signal(Protocol):
    entry: float
    exit: float
    position: int


@dataclass
class StrategyContext:
    data: pd.DataFrame
    cash: float
    position: int
    risk_per_trade: float = 0.01


class BaseStrategy(Protocol):
    name: str

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame: ...

    def position_size(self, context: StrategyContext) -> float:
        if context.data.empty:
            return 0.0
        atr = context.data["atr"].iloc[-1]
        if atr == 0 or pd.isna(atr):
            return 0.0
        dollar_risk = context.cash * context.risk_per_trade
        contracts = dollar_risk / atr
        return max(0.0, contracts)

