#!/usr/bin/env python3
"""Demo script for pair stat-arb using `strategies.statarb.PairStatArb`.
Generates synthetic correlated series, runs the statarb backtest and saves results.
"""
import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from strategies.statarb import PairStatArb


def make_pair_series(x_ticker: str, y_ticker: str, start=None, end=None):
    """Fetch adjusted prices for two tickers from yfinance and return as X/Y DataFrame.

    Raises a SystemExit with a helpful message if yfinance is missing or data is unavailable.
    """
    try:
        import yfinance as yf
    except ImportError:
        raise SystemExit('yfinance not installed. pip install yfinance to run demos with real data')
    df = yf.download([x_ticker, y_ticker], start=start, end=end, progress=False, auto_adjust=True)
    if df is None or df.empty:
        raise SystemExit('yfinance returned no data for given tickers/dates')
    if isinstance(df, pd.Series):
        df = df.to_frame()
    if isinstance(df.columns, pd.MultiIndex):
        try:
            df = df.xs('Close', axis=1, level=0)
        except Exception:
            df = df.droplevel(0, axis=1)
    present = [c for c in [x_ticker, y_ticker] if c in df.columns]
    if len(present) < 2:
        raise SystemExit(f'Downloaded data does not contain requested tickers: {x_ticker}, {y_ticker}')
    df = df[[x_ticker, y_ticker]].dropna()
    df.columns = ['X', 'Y']
    return df


def main():
    import argparse

    p = argparse.ArgumentParser(description="Demo statarb: requires two tickers to fetch via yfinance")
    p.add_argument('--x', type=str, required=True, help='Ticker for X series')
    p.add_argument('--y', type=str, required=True, help='Ticker for Y series')
    p.add_argument('--start', type=str, default=None, help='Start date YYYY-MM-DD')
    p.add_argument('--end', type=str, default=None, help='End date YYYY-MM-DD')
    args = p.parse_args()

    prices = make_pair_series(args.x, args.y, start=args.start, end=args.end)
    arb = PairStatArb(x_symbol="X", y_symbol="Y", lookback=30, entry_z=2.0, exit_z=0.5)
    out = arb.backtest(prices)
    print(out[['zscore','position','pnl']].tail())
    # prefer normalized NAV if present
    plot_series = out['nav'] if 'nav' in out.columns else out['equity']
    plt.figure(figsize=(8, 4))
    plot_series.plot(title='StatArb Equity (normalized nav)')
    plt.ylabel('Equity')
    out_path = Path(__file__).resolve().parent / 'demo_statarb_equity.png'
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f'Saved {out_path}')

if __name__ == '__main__':
    main()
