# Trading Ideas Toolkit

Modular quantitative research toolkit: indicators, backtesting primitives, momentum & statistical arbitrage strategies, factor engine, and performance analytics—packaged with tests for reproducibility.

## Current Features

| Area | Modules | Highlights |
|------|---------|------------|
| Indicators | `indicators/indicator.py` | Bollinger Bands, Stochastic Oscillator |
| Backtest | `backtest/simple.py` | Simple FIFO trade simulation |
| Strategies | `strategies/momentum.py`, `strategies/etf_momentum.py`, `strategies/statarb.py`, `strategies/sector_statarb.py` | Monthly top-N momentum, ETF momentum optimization, pair & multi-pair stat arb |
| Factors | `factors/` + `engines/factor_engine.py` | Momentum, Low Vol, composite ranking, factor portfolio rebalancer |
| Performance | `analytics/performance.py` | Sharpe, CAGR, Max Drawdown, Turnover, summary helper |
| Data | `data/sp500.py` | S&P 500 constituents + price download/cache |

## Repository Layout (flattened src/)
```
src/
  analytics/        # Performance metrics
  backtest/         # Backtesting engines
  data/             # Universe & price helpers
  factors/          # Factor computations & combiners
  engines/          # Portfolio engines (factor)
  indicators/       # Technical indicators
  strategies/       # Strategy implementations
tests/              # Pytest suite
Makefile            # Common dev tasks
pyproject.toml      # Packaging metadata
requirements.txt    # Base deps (optional, pyproject is canonical)
```

## Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev,web]
```

Or with Makefile (after activating env):
```bash
make install
make test
```

## Usage Examples

Momentum (top-N monthly):
```python
import pandas as pd, numpy as np
from strategies import MonthlyTopNMomentum, run_monthly_rebalance

idx = pd.date_range('2024-01-01', periods=260, freq='B')
data = pd.DataFrame({f'T{i}': (1+0.0005*i)**range(len(idx)) for i in range(8)}, index=idx)
res = run_monthly_rebalance(data, MonthlyTopNMomentum(n=4, lookback=120))
print(res.tail())
```

ETF Momentum Optimization:
```python
from strategies import ETFFixedUniverseMomentum, optimize_etf_momentum
best = optimize_etf_momentum(prices, universe=['SPY','QQQ','IWM','EFA','TLT'],
                             param_space={'n':[3,4,5],'lookback':[60,120,180]})
print(best)
```

Factor Portfolio Engine:
```python
from engines import FactorPortfolioEngine, FactorConfig
engine = FactorPortfolioEngine(config=FactorConfig(weights={'momentum':0.6,'low_vol':0.4}, top_n=25))
out = engine.run(prices)
print(out['performance'])
```

Pair Stat Arb:
```python
from strategies import PairStatArb
pair = PairStatArb(x_symbol='X', y_symbol='Y', lookback=60, entry_z=2, exit_z=0.5)
result = pair.backtest(prices[['X','Y']])
```

## Testing
```bash
make test   # or: pytest -q
```

## Performance Metrics
`analytics.performance.summarize_performance(equity, returns, trades)` returns a dict with CAGR, Sharpe, MaxDrawdown, Turnover.

## Roadmap
- Add transaction cost & slippage modeling.
- Extend factor set (value, quality, size) & long/short attribution.
- Turnover-aware rebalancing and position sizing (risk parity / volatility targeting).
- Add CLI entry points for batch runs.
- CI workflow (lint, coverage, type checking) & docs site.

## Data
No bundled CSV datasets. Use the `data.sp500` module to fetch S&P 500 constituents and prices on demand (requires installing with `[web]` extras for `yfinance`, `beautifulsoup4`, `lxml`, `requests`). Supply or construct your own price DataFrames for other universes.

## Disclaimer
Educational research code. Not investment advice.
