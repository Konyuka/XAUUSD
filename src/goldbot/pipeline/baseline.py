"""Wire cached data → features → strategy → backtest."""

from __future__ import annotations

import argparse
from dataclasses import dataclass

from goldbot.backtest import BacktestResult, VectorizedBacktester
from goldbot.data import compute_quality_report, load_cached_prices
from goldbot.features import engineer_feature_set
from goldbot.strategies import DualMovingAverageStrategy
from goldbot.utils.logging import configure_logging


@dataclass(slots=True)
class BaselineResult:
    stats: dict[str, float]
    quality: dict[str, float]
    backtest: BacktestResult


def run_baseline_backtest(symbol: str = "XAUUSD", timeframe: str = "1h") -> BaselineResult:
    """Load cached data, engineer features, run dual-MA backtest."""

    prices = load_cached_prices(symbol=symbol, timeframe=timeframe)
    quality = compute_quality_report(prices, freq=timeframe.upper())
    features = engineer_feature_set(prices)
    strategy = DualMovingAverageStrategy()
    signals = strategy.generate_signals(features)
    backtester = VectorizedBacktester()
    result = backtester.run(signals)
    return BaselineResult(stats=result.stats, quality=quality.__dict__, backtest=result)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run baseline XAUUSD backtest on cached data")
    parser.add_argument("--symbol", default="XAUUSD")
    parser.add_argument("--timeframe", default="1h")
    args = parser.parse_args()

    configure_logging()
    outcome = run_baseline_backtest(symbol=args.symbol, timeframe=args.timeframe)
    print("Quality:", outcome.quality)
    print("Stats:", outcome.stats)


if __name__ == "__main__":
    main()

