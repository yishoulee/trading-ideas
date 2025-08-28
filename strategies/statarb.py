from __future__ import annotations
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict, Any, List


def hedge_ratio(y: pd.Series, x: pd.Series) -> float:
    # simple OLS beta without intercept
    valid = y.notna() & x.notna()
    xv = x[valid]
    yv = y[valid]
    if len(xv) < 2:
        return np.nan
    beta = (xv * yv).sum() / (xv * xv).sum()
    return beta


def zscore(series: pd.Series, window: int) -> pd.Series:
    rolling_mean = series.rolling(window).mean()
    rolling_std = series.rolling(window).std(ddof=0)
    return (series - rolling_mean) / rolling_std

@dataclass
class PairStatArb:
    x_symbol: str
    y_symbol: str
    lookback: int = 60
    entry_z: float = 2.0
    exit_z: float = 0.5

    def generate_signals(self, prices: pd.DataFrame) -> pd.DataFrame:
        x = prices[self.x_symbol]
        y = prices[self.y_symbol]
        beta = hedge_ratio(y, x)
        spread = y - beta * x
        z = zscore(spread, self.lookback)
        long_entry = (z < -self.entry_z).astype(int)
        short_entry = (z > self.entry_z).astype(int)
        exit_sig = (z.abs() < self.exit_z).astype(int)
        # position: +1 long spread (long y short x), -1 short spread
        position = 0
        positions = []
        for le, se, ex in zip(long_entry, short_entry, exit_sig):
            if position == 0:
                if le:
                    position = 1
                elif se:
                    position = -1
            else:
                if ex:
                    position = 0
            positions.append(position)
        out = pd.DataFrame({
            'spread': spread,
            'zscore': z,
            'position': positions
        }, index=prices.index)
        return out

    def backtest(self, prices: pd.DataFrame) -> pd.DataFrame:
        sigs = self.generate_signals(prices)
        x = prices[self.x_symbol]
        y = prices[self.y_symbol]
        beta = hedge_ratio(y, x)
        # daily pnl approximate: position_{t-1} * change in spread_t
        spread = sigs['spread']
        spread_ret = spread.diff().fillna(0)
        sigs['pnl'] = sigs['position'].shift(1).fillna(0) * (-spread_ret)  # negative because long spread profits when spread narrows
        sigs['equity'] = sigs['pnl'].cumsum()
        if len(sigs) > 0:
            cummax = sigs['equity'].cummax()
            sigs['drawdown'] = sigs['equity']/cummax - 1
        return sigs
