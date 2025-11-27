# GOLD: Adaptive XAUUSD Trading Stack

This repo will grow into a research-to-production pipeline for intelligent **XAUUSD** trading. The end goal is a modular bot that can ingest multi-source data, engineer high-signal features, evaluate diversified strategies, and orchestrate execution with strict risk controls.

## Guiding Principles
- **Data-driven**: everything measurable (latency, slippage, drift) gets logged.
- **Modular**: data, features, strategies, risk, and execution stay decoupled so we can swap experiments quickly.
- **Robustness first**: walk-forward validation, Monte Carlo stress, and guardrails outrank headline returns.

## High-Level Architecture
1. **Data Layer**  
   - Raw price feeds (broker, exchange, or CSVs) + macro context (DXY, yields, calendar).  
   - Unified loaders clean, resample, and align series; metadata tracked in catalog.
2. **Feature Layer**  
   - Technical indicators (trend, momentum, volatility, volume proxies) computed via Pandas/`ta`.  
   - Regime detectors (trend strength, volatility buckets) + feature scaling/lagging utilities.
3. **Strategy Layer**  
   - Rule engines describing entries/exits/position sizing.  
   - Library ships with baseline trend-following, breakout, mean reversion, and machine-learning hybrids.
4. **Backtest & Evaluation**  
   - Vectorized engine for fast iteration + optional integration with `backtrader`.  
   - Walk-forward, parameter sweeps, and risk analytics.
5. **Execution & Orchestration**  
   - Broker adapters (MetaTrader/FIX/REST) with latency-aware order routing.  
   - Real-time risk dashboard, alerting, and circuit breakers.

## Tech Stack (initial)
- **Language**: Python 3.11+ (tested with 3.14)
- **Core libs**: `pandas`, `numpy`, `polars`, `ta`, `scikit-learn`, `statsmodels`, `scipy`
- **Backtesting**: custom vectorized engine + `backtrader` bridge
- **Risk/metrics**: `vectorbt`, `empyrical`, custom analytics
- **Config**: `pydantic-settings` (for environment-aware configs), YAML/JSON
- **Logging**: `loguru`
- **Packaging**: `pyproject.toml` + `src/` layout

## Getting Started
1. **Bootstrap environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate             # Windows
   pip install --upgrade pip
   pip install -e .[dev]
   ```
2. **Configure secrets**  
   - Copy `env.example` → `.env`.  
   - Drop in your Twelve Data API key (`GOLD_PROVIDERS__TWELVEDATA_API_KEY`).  
   - Populate MT5 credentials supplied by FBS (`GOLD_MT5__LOGIN`, etc.).

### Fetch historical XAU/USD data via Twelve Data
```bash
python -m goldbot.data.cli --symbol XAU/USD --interval 1h --outputsize 5000
```
This pulls data from Twelve Data, writes a canonical parquet file into `data/raw/`, and can be rerun on demand. The CLI relies on the same config stack, so pass `--symbol XAU/USD` or tweak `.env` for defaults.

### Validate incoming data
- Run the notebook `notebooks/data_quality.ipynb` to ensure there are no missing/duplicate bars and to preview engineered indicators.
- Programmatic helpers live in `goldbot.data.quality` (`load_cached_prices`, `compute_quality_report`) so CI/tests can assert feed health before backtests.

### Run baseline strategy/backtest
```bash
python -m goldbot.pipeline.baseline --symbol XAUUSD --timeframe 1h
```
This loads the cached dataset, engineers indicators, runs the dual moving-average strategy, and prints both feed quality metrics and key performance stats from the vectorized backtester.

### Generate research reports
```bash
python -m goldbot.reporting.baseline_report --symbol XAUUSD --timeframe 1h --output-dir reports
```
Creates JSON snapshots of stats + data quality and a Plotly HTML equity curve under `reports/`, ready to share or attach to notebooks.

Open `notebooks/performance_insights.ipynb` to load those artifacts, inspect stats inline, and re-render interactive equity curves inside Jupyter.

### MT5 (FBS) integration
- Add your MT5 demo/live credentials to `.env`.
- Use `goldbot.execution.MT5Adapter` to connect:
  ```python
  from goldbot.execution import MT5Adapter

  adapter = MT5Adapter()
  adapter.connect()
  adapter.place_market_order("buy", volume=1.0)
  adapter.shutdown()
  ```
- The adapter wraps the official `MetaTrader5` Python API and aligns with the FBS-Demo server out of the box.

### MT5 Smoke Test CLI
Before running live logic, sanity-check the connection (optionally place a micro-order):
```bash
python -m goldbot.execution.smoke --place-order --side buy --volume 0.01
```
Omit `--place-order` to only verify login/account info without executing trades.

## Immediate Roadmap
1. Scaffold package + baseline utilities (this commit).  
2. Implement data ingestion with sample CSVs and diagnostic notebook.  
3. Add feature engineering module with indicator suites and tests.  
4. Code baseline strategies + shared position sizing helpers.  
5. Ship vectorized backtester with walk-forward harness + reporting.  
6. Integrate broker/execution stubs, then connect to paper trading environment.

## Contributing Workflow
1. Create a feature branch per experiment.  
2. Add tests/notebooks demonstrating behavior.  
3. Keep configs in `configs/` (per environment) and secrets in `.env` (never committed).  
4. Run lint/tests via `make check` (to be added).  

## Next Steps
- Extend CLI to support incremental sync + WebSocket streaming.
- Add notebook-based diagnostics for fetched data and indicator suites.
- Finish MT5 risk controls (exposure caps, heartbeat monitoring) and connect to execution orchestrator.

_Let’s iterate relentlessly while keeping each layer testable and observable._

