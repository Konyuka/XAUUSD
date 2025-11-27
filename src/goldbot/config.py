"""Centralized configuration powered by pydantic-settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DataPaths(BaseModel):
    raw_dir: Path = Field(default=Path("data/raw"))
    processed_dir: Path = Field(default=Path("data/processed"))
    cache_dir: Path = Field(default=Path("data/cache"))


class BacktestConfig(BaseModel):
    initial_capital: float = 100_000.0
    commission_perc: float = 0.0002  # 2 bps
    slippage_bps: float = 0.5
    risk_free_rate: float = 0.01


class StrategyUniverse(BaseModel):
    symbols: tuple[str, ...] = ("XAUUSD",)
    base_timeframes: tuple[str, ...] = ("1H", "4H", "1D")
    execution_timeframe: str = "15M"


class DataProviderSettings(BaseModel):
    twelvedata_api_key: Optional[str] = None
    default_symbol: str = "XAU/USD"
    default_interval: str = "1h"
    outputsize: int = 5000


class MT5Credentials(BaseModel):
    server: str = "FBS-Demo"
    login: Optional[int] = None
    password: Optional[str] = None
    symbol: str = "XAUUSD"


class Settings(BaseSettings):
    """Environment-aware settings container."""

    model_config = SettingsConfigDict(env_prefix="GOLD_", env_file=".env", env_nested_delimiter="__")

    environment: Literal["dev", "staging", "prod"] = "dev"
    data: DataPaths = DataPaths()
    backtest: BacktestConfig = BacktestConfig()
    universe: StrategyUniverse = StrategyUniverse()
    providers: DataProviderSettings = DataProviderSettings()
    mt5: MT5Credentials = MT5Credentials()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""

    settings = Settings()
    settings.data.raw_dir.mkdir(parents=True, exist_ok=True)
    settings.data.processed_dir.mkdir(parents=True, exist_ok=True)
    settings.data.cache_dir.mkdir(parents=True, exist_ok=True)
    return settings


settings = get_settings()

