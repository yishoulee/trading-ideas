# Statistical Arbitrage on Sector ETFs

## Overview
This project implements a statistical arbitrage trading strategy focusing on sector ETFs. It uses both traditional pairs trading and machine learning-enhanced approaches to identify and exploit temporary price discrepancies between correlated ETF pairs.

## Features
- ETF correlation analysis to identify suitable trading pairs
- Traditional pairs trading implementation with customizable parameters
- Machine learning-enhanced pairs trading with parameter optimization
- Comprehensive backtesting and performance visualization
- Time series cross-validation for robust parameter selection

## Requirements
```python
pandas
numpy
yfinance
scipy
scikit-learn
matplotlib
seaborn
```

## Installation
```bash
pip install pandas numpy yfinance scipy scikit-learn matplotlib seaborn
```

## Usage

### 1. ETF Correlation Analysis
```python
# Example of analyzing ETF correlations
etfs = ['SPY', 'QQQ', 'IWM', 'EFA', 'EEM', 'GLD', 'TLT', 'VNQ']
results = analyze_etf_correlations(etfs, start_date='2020-01-01', end_date='2024-01-01')
```

### 2. Traditional Pairs Trading
```python
# Initialize and run traditional pairs trading strategy
trader = PairsTrader(
    symbol1='SPY',
    symbol2='QQQ',
    start_date='2020-01-01',
    end_date='2024-01-01',
    entry_threshold=2.0,
    exit_threshold=0.3,
    lookback_period=60
)

trader.calculate_spread()
trader.generate_signals()
trader.backtest_strategy()
```

### 3. ML-Enhanced Pairs Trading
```python
# Initialize and run ML-enhanced pairs trading
ml_trader = MLPairsTrader(
    symbol1='SPY',
    symbol2='QQQ',
    start_date='2020-01-01',
    end_date='2024-01-01'
)

best_params = ml_trader.optimize_parameters(cv_splits=5)
```

## Strategy Parameters
- `entry_threshold`: Z-score threshold for entering positions
- `exit_threshold`: Z-score threshold for exiting positions
- `lookback_period`: Rolling window size for calculating statistics
- Additional parameters optimized through machine learning approach

## Performance Metrics
- Total Return
- Annual Return
- Sharpe Ratio
- Maximum Drawdown
- Win Rate

## Visualization
The project includes comprehensive visualization tools:
- ETF price movements
- Z-score signals
- Trading positions
- Cumulative returns
- Drawdown analysis

Example visualization code can be found here:
```python:Statistical Arbitrage on Sector ETFs.ipynb
startLine: 188
endLine: 213
```

## Notes
- Past performance does not guarantee future results
- Transaction costs and slippage are not included in the backtest
- Always perform proper risk management when implementing trading strategies