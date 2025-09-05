from __future__ import annotations
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict, Any, List

from utils import zscore as _zscore


def hedge_ratio(y: pd.Series, x: pd.Series) -> float:
    """Estimate simple hedge ratio (beta) of y ~ x without intercept.

    Returns the slope estimate from OLS constrained through the origin.
    """
    valid = y.notna() & x.notna()
    xv = x[valid]
    yv = y[valid]
    if len(xv) < 2:
        return np.nan
    beta = (xv * yv).sum() / (xv * xv).sum()
    return beta

@dataclass
class PairStatArb:
    x_symbol: str
    y_symbol: str
    lookback: int = 60
    entry_z: float = 2.0
    exit_z: float = 0.5
    initial_capital: float = 1.0

    def generate_signals(self, prices: pd.DataFrame) -> pd.DataFrame:
        """Generate z-score, entry/exit signals and discrete positions for a pair.

        Returns a DataFrame with columns: spread, zscore, position (integer -1/0/1).
        """
        x = prices[self.x_symbol]
        y = prices[self.y_symbol]
        beta = hedge_ratio(y, x)
        spread = y - beta * x
        z = _zscore(spread, window=self.lookback)
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
        """Run a simple backtest: position_{t-1} * change in spread_t as daily P&L.

        Returns a DataFrame with columns: spread, zscore, position, pnl, equity, drawdown.
        """
        sigs = self.generate_signals(prices)
        x = prices[self.x_symbol]
        y = prices[self.y_symbol]
        beta = hedge_ratio(y, x)

        # daily pnl approximate: position_{t-1} * change in spread_t
        spread = sigs['spread']
        spread_ret = spread.diff().fillna(0)
        raw_pnl = sigs['position'].shift(1).fillna(0) * (-spread_ret)  # negative because long spread profits when spread narrows
        sigs['pnl'] = raw_pnl

        # Keep legacy equity as cumulative P&L (preserves previous behavior/tests)
        sigs['equity'] = sigs['pnl'].cumsum()

        # Compute normalized NAV for demo/analysis: estimate returns using notional
        prev_y = y.shift(1)
        prev_x = x.shift(1)
        notional = (prev_y.abs() + (abs(beta) * prev_x.abs())).fillna(0)
        returns = pd.Series(0.0, index=sigs.index)
        mask = notional > 0
        returns.loc[mask] = raw_pnl.loc[mask] / notional.loc[mask]
        nav = (1.0 + returns).cumprod() * float(self.initial_capital)
        sigs['returns'] = returns
        sigs['nav'] = nav

        if len(sigs) > 0:
            cummax = sigs['equity'].cummax()
            sigs['drawdown'] = sigs['equity'] / cummax - 1
        return sigs
