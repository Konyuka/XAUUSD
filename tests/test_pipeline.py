import pandas as pd

from goldbot.pipeline.baseline import run_baseline_backtest


def test_run_baseline_backtest(monkeypatch):
    idx = pd.date_range("2024-01-01", periods=200, freq="H", tz="UTC")
    df = pd.DataFrame(
        {
            "open": range(200),
            "high": range(1, 201),
            "low": range(200),
            "close": range(200),
            "volume": 1,
        },
        index=idx,
    )

    monkeypatch.setattr("goldbot.pipeline.baseline.load_cached_prices", lambda **_: df)
    result = run_baseline_backtest(symbol="XAUUSD", timeframe="1h")
    assert "cagr" in result.stats
    assert result.quality["n_rows"] == len(df)
    assert hasattr(result.backtest, "equity_curve")

