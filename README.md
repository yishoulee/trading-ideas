# ETF Momentum Trading Strategy with Technical Indicators

## Overview
This project implements and backtests a momentum trading strategy for ETFs using ADX (Average Directional Index) and Stochastic Oscillator indicators. The strategy includes parameter optimization to find the most effective combination of technical indicator settings.

## Features
- Automated data fetching using yfinance
- Technical indicator calculations:
  - Average Directional Index (ADX)
  - Stochastic Oscillator
- Parameter optimization for:
  - ADX period
  - Stochastic K period
  - Stochastic D period
- Performance visualization:
  - Portfolio value over time
  - Technical indicator plots
  - 3D parameter optimization results

## Requirements
```
pandas
numpy
matplotlib
yfinance
```

## Installation
```bash
pip install pandas numpy matplotlib yfinance
```

## Usage
1. Import the required libraries:
```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
from datetime import datetime
```

2. Load ETF data using yfinance:
```python
etf_data = yf.download('SPY')  # Replace with your desired ETF ticker
```

3. Calculate technical indicators and generate trading signals:
```python
data = calculate_adx(etf_data, period=14)
data = calculate_stochastic_oscillator(data, k_period=14, d_period=3)
data = generate_signals(data)
```

4. Optimize parameters and backtest the strategy:
```python
results = optimize_parameters(data, adx_periods, stoch_k_periods, stoch_d_periods)
best_params = max(results, key=lambda x: x[3])
```

## Strategy Logic
- The strategy combines ADX and Stochastic Oscillator signals:
  - Buy signals occur when:
    - ADX > 20 and +DI > -DI
    - Stochastic %K < 20 with bullish crossover
  - Sell signals occur when:
    - ADX > 20 and -DI > +DI
    - Stochastic %K > 80 with bearish crossover

## Performance Metrics
- The strategy's performance is evaluated using:
  - Sharpe Ratio
  - Portfolio value over time
  - Visual analysis of indicator signals

## Visualization
The project includes various visualization tools:
- Portfolio value charts
- Technical indicator plots
- 3D parameter optimization surface plots

## Disclaimer
This project is for educational purposes only. Trading involves risk, and past performance does not guarantee future results. Always conduct your own research and consider seeking professional financial advice before making investment decisions.