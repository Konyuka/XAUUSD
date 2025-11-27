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
- **Language**: Python 3.11+
- **Core libs**: `pandas`, `numpy`, `polars`, `ta`, `scikit-learn`, `statsmodels`, `scipy`
- **Backtesting**: custom vectorized engine + `backtrader` bridge
- **Risk/metrics**: `vectorbt`, `empyrical`, custom analytics
- **Config**: `pydantic-settings` (for environment-aware configs), YAML/JSON
- **Logging**: `structlog` or `loguru`
- **Packaging**: `pyproject.toml` + `src/` layout

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
- Finalize dependency versions in `pyproject.toml`.  
- Populate `src/goldbot` modules (data loaders, indicator toolkit, strategy interfaces, backtest engine).  
- Prepare sample datasets and notebooks for exploratory analysis.  

_Let’s iterate relentlessly while keeping each layer testable and observable._

