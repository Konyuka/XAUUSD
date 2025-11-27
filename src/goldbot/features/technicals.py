"""Feature engineering utilities using pandas + ta."""

from __future__ import annotations

import pandas as pd
import ta


def add_trend_indicators(df: pd.DataFrame, fast: int = 21, slow: int = 55) -> pd.DataFrame:
    df = df.copy()
    df[f"sma_{fast}"] = df["close"].rolling(fast).mean()
    df[f"sma_{slow}"] = df["close"].rolling(slow).mean()
    df["ema_fast"] = df["close"].ewm(span=fast, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=slow, adjust=False).mean()
    df["adx"] = ta.trend.adx(df["high"], df["low"], df["close"])
    return df


def add_momentum_indicators(df: pd.DataFrame, rsi_period: int = 14) -> pd.DataFrame:
    df = df.copy()
    df["rsi"] = ta.momentum.rsi(df["close"], window=rsi_period)
    df["stoch_k"] = ta.momentum.stoch(df["high"], df["low"], df["close"])
    df["stoch_d"] = df["stoch_k"].rolling(3).mean()
    return df


def add_volatility_indicators(df: pd.DataFrame, atr_period: int = 14) -> pd.DataFrame:
    df = df.copy()
    df["atr"] = ta.volatility.average_true_range(df["high"], df["low"], df["close"], window=atr_period)
    bb = ta.volatility.BollingerBands(close=df["close"], window=20, window_dev=2)
    df["bb_high"] = bb.bollinger_hband()
    df["bb_low"] = bb.bollinger_lband()
    df["bb_pct"] = bb.bollinger_pband()
    return df


def engineer_feature_set(df: pd.DataFrame) -> pd.DataFrame:
    """Return dataframe with trend, momentum, and volatility features."""

    engineered = add_trend_indicators(df)
    engineered = add_momentum_indicators(engineered)
    engineered = add_volatility_indicators(engineered)
    engineered.dropna(inplace=True)
    return engineered

