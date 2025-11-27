# Architecture Blueprint

## Layered Overview

| Layer | Responsibility | Key Modules |
| --- | --- | --- |
| Data | Ingest & normalize multi-source bars + macro | `goldbot.data.loaders` |
| Features | Engineer technical + regime signals | `goldbot.features` |
| Strategies | Encode entry/exit/position logic | `goldbot.strategies` |
| Backtest | Evaluate, stress, and score strategies | `goldbot.backtest` |
| Execution | Route trades, enforce risk, monitor | `goldbot.execution` |

## Data Flow
1. **Raw Feeds** land in `data/raw/` (CSV, API pull, etc.).  
2. **Loaders** clean + resample into canonical OHLCV frames.  
3. **Feature Engine** appends indicators → `engineer_feature_set`.  
4. **Strategy** consumes enriched frame to produce `position` series.  
5. **Backtester** evaluates performance, risk, and guardrails.  
6. **Execution** consumes live signals once promoted from research.

## Extensibility Points
- **Adapters**: implement new loaders or broker clients by following the dataclass patterns already sketched.  
- **Indicators**: add functions to `features/` and wire them into `engineer_feature_set`.  
- **Strategies**: inherit from the `BaseStrategy` protocol and register in `strategies/__init__.py`.  
- **Risk Controls**: extend `config.BacktestConfig` and consumption sites when we slot in live execution.

## Next Milestones
1. Wire actual data source (CSV + API) and add sample dataset.  
2. Introduce tests covering indicators + strategy signals.  
3. Expand backtester with transaction cost modeling + trade ledger.  
4. Add orchestration CLI / notebook for research loops.  
5. Instrument logging + metrics for observability.

