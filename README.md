# Trading Ideas (Unified)

A consolidated collection of my early algorithmic / quantitative trading explorations (Bollinger Bands, Stochastic Oscillator, ETF momentum, sector statistical arbitrage) refactored into a coherent, minimal, and testable Python package plus research notebooks.

## Repo Layout

```
trading_ideas/              # Reusable library code (indicators, backtests, utils)
  indicators/               # Technical indicator functions
  backtest/                 # Simple backtesting engines
  data/                     # (Optional) local static data samples
strategies/                 # Strategy research notebooks (exploratory)
engines/                    # Legacy / prototype scripts
requirements.txt            # Minimal runtime + test deps
pyproject.toml              # Packaging metadata
```

## Quick Start

1. Create environment & install deps:
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .  # optional if packaging later
```
2. Run tests:
```
pytest -q
```
3. Open the notebooks in `strategies/` for exploratory analysis. Logic formerly in the removed legacy notebook has been modularized into the package modules.

## Indicators Implemented
- Bollinger Bands (`bollinger_bands`)
- Stochastic Oscillator (`stochastic_oscillator`)

## Backtesting
`SimpleFIFOBacktester` offers a light position management loop (FIFO close, fraction-of-cash sizing) for fast prototyping. Signals are integers: -1 buy, +1 sell, 0 hold. Extend or replace for more realism (slippage, fees, latency, risk limits).

## Next Improvements
- Shift signals by one bar to avoid look-ahead bias.
- Add performance metrics (returns, drawdown, Sharpe proxy, win rate).
- Parameter sweep utilities & walk-forward validation.
- Data acquisition layer with provenance + schema validation.
- Vectorized position accounting & transaction cost modeling.
- Packaging (`pyproject.toml`) and CI workflow (lint, tests).

## Data
`ETH-USD.csv` is sample historical data (source: Yahoo Finance). Add multiple assets / asset classes as needed; store only *small* slices for examples.

## Disclaimer
Educational / research prototype only. Not investment advice.
