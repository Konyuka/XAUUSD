"""Produce serialized + visual reports from baseline runs."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import plotly.graph_objs as go

from goldbot.pipeline.baseline import BaselineResult, run_baseline_backtest
from goldbot.utils.logging import configure_logging


@dataclass(slots=True)
class ReportArtifacts:
    stats_path: Path
    quality_path: Path
    equity_plot_path: Path


def generate_baseline_report(
    symbol: str = "XAUUSD",
    timeframe: str = "1h",
    output_dir: Path | None = None,
) -> ReportArtifacts:
    """Run baseline pipeline and persist stats + equity curve figure."""

    outcome = run_baseline_backtest(symbol=symbol, timeframe=timeframe)
    stats_path, quality_path, equity_path = _write_artifacts(outcome, output_dir)
    return ReportArtifacts(stats_path=stats_path, quality_path=quality_path, equity_plot_path=equity_path)


def _write_artifacts(outcome: BaselineResult, output_dir: Path | None):
    out_dir = output_dir or Path("reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    stats_path = out_dir / "baseline_stats.json"
    quality_path = out_dir / "baseline_quality.json"
    equity_path = out_dir / "baseline_equity.html"

    stats_path.write_text(json.dumps(outcome.stats, indent=2))
    quality_path.write_text(json.dumps(outcome.quality, indent=2, default=str))

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=outcome.backtest.equity_curve.index,
            y=outcome.backtest.equity_curve.values,
            mode="lines",
            name="Equity",
        )
    )
    figure.update_layout(title="Baseline Equity Curve", xaxis_title="Date", yaxis_title="Equity (USD)")
    figure.write_html(equity_path)
    return stats_path, quality_path, equity_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate baseline backtest report artifacts.")
    parser.add_argument("--symbol", default="XAUUSD")
    parser.add_argument("--timeframe", default="1h")
    parser.add_argument("--output-dir", default="reports")
    args = parser.parse_args()

    configure_logging()
    artifacts = generate_baseline_report(
        symbol=args.symbol,
        timeframe=args.timeframe,
        output_dir=Path(args.output_dir),
    )
    print("Report artifacts saved:", artifacts)


if __name__ == "__main__":
    main()

