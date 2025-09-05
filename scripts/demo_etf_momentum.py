#!/usr/bin/env python3
"""Demo script for ETF momentum runner using `strategies.etf_momentum.run_etf_momentum`.
Creates synthetic ETF price data and runs `run_etf_momentum`.
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

from strategies.etf_momentum import ETFFixedUniverseMomentum, run_etf_momentum


def make_price_panel(tickers, start=None, end=None):
    """Fetch prices for tickers using yfinance. Exits if yfinance missing or data is unavailable."""
    try:
        import yfinance as yf
    except ImportError:
        raise SystemExit('yfinance not installed. pip install yfinance to run demos with real data')
    df = yf.download(tickers, start=start, end=end, progress=False, auto_adjust=True)
    if df is None or df.empty:
        raise SystemExit('yfinance returned no data for given tickers/dates')
    if isinstance(df, pd.Series):
        df = df.to_frame()
    if isinstance(df.columns, pd.MultiIndex):
        try:
            df = df.xs('Close', axis=1, level=0)
        except Exception:
            df = df.droplevel(0, axis=1)
    present = [c for c in tickers if c in df.columns]
    if not present:
        raise SystemExit('Downloaded data does not contain requested tickers')
    return df[present].dropna()


def main():
    import argparse

    p = argparse.ArgumentParser(description="Demo ETF momentum: requires tickers to fetch via yfinance")
    p.add_argument('--tickers', nargs='+', required=True, help='List of tickers to fetch')
    p.add_argument('--start', type=str, default=None, help='Start date YYYY-MM-DD')
    p.add_argument('--end', type=str, default=None, help='End date YYYY-MM-DD')
    args = p.parse_args()

    prices = make_price_panel(args.tickers, start=args.start, end=args.end)
    cfg = ETFFixedUniverseMomentum(universe=prices.columns.tolist(), n=3, lookback=60)
    out = run_etf_momentum(prices, cfg, initial_capital=10000)
    print('Performance:', out['performance'])
    out_path = Path(__file__).resolve().parent / 'demo_etf_momentum_equity.png'
    out['equity_curve']['equity'].plot(title='ETF Momentum Equity')
    plt.ylabel('Equity')
    plt.tight_layout()
    plt.savefig(out_path)
    print(f'Saved {out_path}')

if __name__ == '__main__':
    main()
