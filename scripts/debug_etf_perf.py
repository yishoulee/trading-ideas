#!/usr/bin/env python3
"""Debug helper: run ETF momentum and print diagnostics about returns and sharpe.
"""
import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
from strategies.etf_momentum import ETFFixedUniverseMomentum, run_etf_momentum
from analytics import performance


def infer_ppy_from_index(idx: pd.Index) -> int:
    if idx is None or len(idx) < 2:
        return 252
    # convert index to a DatetimeIndex and compute day deltas
    dt_index = pd.DatetimeIndex(idx)
    deltas = dt_index.to_series().diff().dropna().dt.days
    if deltas.empty:
        return 252
    med = float(deltas.median())
    if med <= 0:
        return 252
    ppy = int(round(365.25 / med))
    return ppy


def main():
    import argparse
    p = argparse.ArgumentParser(description='Debug ETF momentum perf')
    p.add_argument('--tickers', nargs='+', required=True)
    p.add_argument('--start', type=str, default='2023-01-01')
    p.add_argument('--end', type=str, default='2024-01-01')
    args = p.parse_args()

    cfg = ETFFixedUniverseMomentum(universe=args.tickers, n=3, lookback=60)
    out = run_etf_momentum(pd.DataFrame(), cfg, initial_capital=50000) if False else None
    # run_etf_momentum expects a prices DataFrame; use the function here by fetching prices with yfinance
    try:
        import yfinance as yf
    except ImportError:
        print('yfinance not installed; cannot fetch real data')
        return
    df = yf.download(args.tickers, start=args.start, end=args.end, progress=False, auto_adjust=True)
    # handle multiindex
    if isinstance(df, pd.Series):
        df = df.to_frame()
    if isinstance(df.columns, pd.MultiIndex):
        try:
            df = df.xs('Close', axis=1, level=0)
        except Exception:
            df = df.droplevel(0, axis=1)
    df = df[[c for c in args.tickers if c in df.columns]].dropna()
    cfg = ETFFixedUniverseMomentum(universe=df.columns.tolist(), n=3, lookback=60)
    out = run_etf_momentum(df, cfg, initial_capital=50000)
    eq = out['equity_curve']['equity'] if 'equity_curve' in out and 'equity' in out['equity_curve'] else out['equity_curve'].get('equity') if isinstance(out['equity_curve'], pd.DataFrame) else None
    if eq is None:
        print('No equity returned; abort')
        return
    rets = out['equity_curve'].get('returns') if isinstance(out['equity_curve'], pd.DataFrame) and 'returns' in out['equity_curve'] else eq.pct_change().fillna(0)

    print('Equity index sample:', eq.index[:6])
    print('Num observations:', len(rets))
    print('Returns head:')
    print(rets.head(10))
    print('\nReturns stats: mean, std, describe')
    mean = rets.mean()
    std = rets.std(ddof=0)
    print('mean=', mean, 'std=', std)
    print(rets.describe())
    ppy = infer_ppy_from_index(eq.index)
    print('Inferred periods-per-year (ppy)=', ppy)
    print('Sharpe using analytics.sharpe_ratio:', performance.sharpe_ratio(rets))
    # manual calc
    if std > 0:
        print('Manual Sharpe:', (mean * (ppy**0.5)) / std)
    else:
        print('Std is zero; cannot compute manual Sharpe')

if __name__ == '__main__':
    main()
