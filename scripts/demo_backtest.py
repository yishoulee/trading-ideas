#!/usr/bin/env python3
"""Minimal demo script to run a small backtest using the repo's SimpleFIFOBacktester.

Saves an equity curve image to `demo_equity.png` and prints a short summary.
"""

import sys
from pathlib import Path

# Ensure the repository root is on sys.path so imports like `from backtest.simple` work
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from backtest.simple import SimpleFIFOBacktester


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Demo backtest: requires a single ticker to fetch via yfinance")
    p.add_argument('--ticker', type=str, required=True, help='Ticker symbol to fetch price for')
    p.add_argument('--start', type=str, default=None, help='Start date YYYY-MM-DD')
    p.add_argument('--end', type=str, default=None, help='End date YYYY-MM-DD')
    args = p.parse_args()

    try:
        import yfinance as yf
    except ImportError:
        raise SystemExit('yfinance not installed. pip install yfinance to run demos with real data')

    df = yf.download(args.ticker, start=args.start, end=args.end, progress=False, auto_adjust=True)
    if df is None or df.empty:
        raise SystemExit('yfinance returned no data for ticker and dates provided')
    if isinstance(df, pd.Series):
        df = df.to_frame()
    if isinstance(df.columns, pd.MultiIndex):
        try:
            df = df.xs('Close', axis=1, level=0)
        except Exception:
            df = df.droplevel(0, axis=1)
    if args.ticker not in df.columns:
        # sometimes yfinance returns with single column 'Adj Close' index — try that
        # fall back to first numeric column
        series = df.select_dtypes(include=['number']).iloc[:, 0]
        prices = pd.Series(series.values, index=series.index, name='price')
    else:
        prices = pd.Series(df[args.ticker].values, index=df.index, name='price')

    # simple signals: buy on >1% drop, sell on >1% rise
    pct = prices.pct_change().fillna(0)
    signals = pd.Series(0, index=prices.index)
    signals[pct < -0.01] = -1
    signals[pct > 0.01] = 1

    # run the backtester
    bt = SimpleFIFOBacktester(
        initial_cash=10000.0, trade_fraction=0.2, min_cash=1.0, commission_bps=5.0, slippage_bps=2.0
    )
    equity = bt.run(prices, signals)

    # summary
    print("Final equity:", equity.iloc[-1])
    print("Cash:", bt.cash)
    print("Cost paid:", bt.cost_paid)
    print("Open trades:", len(bt.open_trades))

    # save plot
    plt.figure(figsize=(8, 4))
    plt.plot(equity.index, equity.values, label="Equity")
    plt.xlabel("Date")
    plt.ylabel("Equity")
    plt.title("Demo Equity Curve")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    out_path = Path(__file__).resolve().parent / "demo_equity.png"
    plt.savefig(out_path)
    print(f"Saved plot to {out_path}")


if __name__ == "__main__":
    main()
