# strategies

This folder contains strategy implementations, experiment helpers, and small utilities for running strategy simulations.

Files
- `__init__.py` — package initializer (keeps `strategies` importable).
- `momentum.py` — core momentum strategy and engine:
  - `MonthlyTopNMomentum(n, lookback)` — selection logic based on trailing returns.
  - `MomentumRebalanceEngine(strategy, initial_capital)` — calendar monthly rebalance engine that logs trades and equity history.
  - `run_monthly_rebalance(prices, strategy, initial_capital)` — thin wrapper for backwards compatibility.
- `etf_momentum.py` — ETF-focused experiment harness on top of the momentum engine:
  - `ETFFixedUniverseMomentum(universe, n, lookback)` — config -> strategy adapter.
  - `run_etf_momentum(prices, config, initial_capital)` — runs the engine and returns performance + trades.
  - `optimize_etf_momentum(prices, universe, param_space, top_k)` — grid-search helper that returns top candidates.
- `statarb.py` — pair/statistical-arbitrage utilities and a backtest harness (mean-reversion style signals).
- `sector_statarb.py` — multi-pair or sector-level stat arb helper (team-level orchestration for multiple pairs).

Why modules are separate
- Each file has a single responsibility: the momentum modules perform ranking + rebalance, while statarb modules handle pair construction, z-score entry/exit and hedged P&L.
- `etf_momentum.py` intentionally wraps the core momentum engine to provide experiment plumbing (filters, parameter sweeps, summaries).

Quick usage examples

From Python REPL or a script:

```py
import pandas as pd
from strategies.momentum import MonthlyTopNMomentum, MomentumRebalanceEngine, run_monthly_rebalance
from strategies.etf_momentum import ETFFixedUniverseMomentum, run_etf_momentum

# prices: a DataFrame with a DatetimeIndex and tickers as columns
# Example: run the core momentum engine
strategy = MonthlyTopNMomentum(n=10, lookback=252)
# engine = MomentumRebalanceEngine(strategy=strategy, initial_capital=10000)
# results = engine.run(prices)

# Or use the ETF helper if you have a fixed universe
cfg = ETFFixedUniverseMomentum(universe=['SPY','QQQ','IWM'], n=2, lookback=252)
out = run_etf_momentum(prices, cfg)
print(out['performance'])
```