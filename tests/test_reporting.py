from pathlib import Path

import pandas as pd

from goldbot.backtest.engine import BacktestResult
from goldbot.pipeline.baseline import BaselineResult
from goldbot.reporting.baseline_report import generate_baseline_report


def test_generate_baseline_report(monkeypatch, tmp_path):
    idx = pd.date_range("2024-01-01", periods=50, freq="H", tz="UTC")
    dummy_result = BacktestResult(
        equity_curve=pd.Series(range(50), index=idx, name="equity"),
        trades=pd.DataFrame(),
        stats={"cagr": 0.1},
    )
    baseline = BaselineResult(stats={"cagr": 0.1}, quality={"n_rows": 50}, backtest=dummy_result)
    monkeypatch.setattr("goldbot.reporting.baseline_report.run_baseline_backtest", lambda **_: baseline)

    artifacts = generate_baseline_report(output_dir=tmp_path)
    assert Path(artifacts.stats_path).exists()
    assert Path(artifacts.equity_plot_path).exists()

