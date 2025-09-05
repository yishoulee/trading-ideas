#!/usr/bin/env python3
"""Demo factor model: compute momentum factor and composite ranking across tickers.

Creates `demo_factors.csv` and `demo_factors.png`.
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

from factors.momentum import momentum_factor
from factors.core import composite_rank
from datetime import timedelta


def make_price_panel(tickers, start=None, end=None):
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


def fetch_prices_yf(tickers, start=None, end=None):
    try:
        import yfinance as yf
    except ImportError:
        raise RuntimeError("yfinance not installed; pip install yfinance to fetch real data")
    df = yf.download(tickers, start=start, end=end, progress=False, auto_adjust=True)
    if isinstance(df, pd.Series):
        df = df.to_frame()
    if isinstance(df.columns, pd.MultiIndex):
        try:
            df = df.xs('Close', axis=1, level=0)
        except Exception:
            df = df.droplevel(0, axis=1)
    present = [c for c in tickers if c in df.columns]
    if not present:
        raise RuntimeError('No requested tickers found in yfinance result')
    return df[present].dropna()


def main():
    import argparse

    p = argparse.ArgumentParser(description='Demo factor model: compute momentum & composite rank')
    p.add_argument('--use-yfinance', action='store_true', help='Fetch real data from yfinance')
    p.add_argument('--tickers', nargs='+', help='Tickers to fetch or simulate')
    p.add_argument('--start', type=str, default=None)
    p.add_argument('--end', type=str, default=None)
    p.add_argument('--lookback', type=int, default=120)
    p.add_argument('--top', type=int, default=10, help='How many top tickers to print')
    args = p.parse_args()

    if not args.tickers:
        raise SystemExit('Provide --tickers for demos using real data')
    prices = make_price_panel(args.tickers, start=args.start, end=args.end)

    # compute momentum factor (cross-section for last date)
    mom = momentum_factor(prices, lookback=args.lookback)
    factors = {'momentum': mom}
    weights = {'momentum': 1.0}

    ranked = composite_rank(factors, weights)
    # Save CSV
    out_df = pd.DataFrame({'rank_score': ranked})
    out_path_csv = Path(__file__).resolve().parent / 'demo_factors.csv'
    out_df.to_csv(out_path_csv)

    # Plot top N scores
    topn = ranked.head(args.top)
    plt.figure(figsize=(8, 4))
    topn.sort_values().plot(kind='barh')
    plt.title('Top factor scores (composite rank)')
    plt.xlabel('Score')
    plt.tight_layout()
    out_path_png = Path(__file__).resolve().parent / 'demo_factors.png'
    plt.savefig(out_path_png)

    print(f'Saved {out_path_csv} and {out_path_png}')
    print('Top tickers:')
    print(topn.head(args.top))

    # === minimal backtest: equal-weight top-N monthly rebalancer ===
    top_n = args.top if args.top <= len(prices.columns) else len(prices.columns)
    # build monthly rebalance dates from prices index
    monthly = prices.resample('MS').first().index
    equity = []
    dates = []
    cash = args.top * 0.0
    current_holdings = {}
    portfolio_value = 1.0
    for i, dt in enumerate(monthly):
        # find nearest trading date
        pos = prices.index.get_indexer([dt], method='nearest')[0]
        if pos <= 0:
            continue
        # compute factors at this date by using data up to pos
        window_prices = prices.iloc[: pos+1]
        mom_cs = momentum_factor(window_prices, lookback=args.lookback)
        ranked_cs = composite_rank({'momentum': mom_cs}, {'momentum': 1.0})
        top_list = ranked_cs.head(top_n).index.tolist()
        # determine prices at rebalance and next rebalance
        start_price = prices.loc[prices.index[pos], top_list]
        next_dt = monthly[i+1] if i < len(monthly)-1 else prices.index[-1]
        next_pos = prices.index.get_indexer([next_dt], method='nearest')[0]
        end_price = prices.iloc[next_pos][top_list]
        # equal weight allocation
        shares = {t: (1.0 / top_n) / start_price[t] for t in top_list}
        # compute portfolio value at end of period
        portfolio_value = sum(shares[t] * end_price[t] for t in top_list)
        equity.append(portfolio_value)
        dates.append(prices.index[next_pos])

    if equity:
        eq_series = pd.Series(equity, index=pd.DatetimeIndex(dates), name='equity')
        # normalize to start at 1.0
        eq_series = eq_series / eq_series.iloc[0]
        out_eq_path = Path(__file__).resolve().parent / 'demo_factors_equity.png'
        plt.figure(figsize=(8, 4))
        eq_series.plot(title=f'Top-{top_n} equal-weight monthly equity')
        plt.ylabel('Normalized Equity')
        plt.tight_layout()
        plt.savefig(out_eq_path)
        plt.close()
        print(f'Saved backtest equity to {out_eq_path}')


if __name__ == '__main__':
    main()
