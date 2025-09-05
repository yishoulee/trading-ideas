from __future__ import annotations
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
from .statarb import hedge_ratio
from utils import zscore as _zscore
from analytics.performance import summarize_performance

@dataclass
class PairDefinition:
    x: str
    y: str
    lookback: int = 60
    entry_z: float = 2.0
    exit_z: float = 0.5
    """Lightweight container defining a single pair to trade.

    Attributes
    - x, y: ticker symbols for the pair (x is the hedge leg, y is the asset leg).
    - lookback: rolling window for z-score
    - entry_z, exit_z: z-score thresholds for entry/exit
    """

@dataclass
class MultiPairStatArb:
    pairs: List[PairDefinition]
    capital: float = 100_000
    per_pair_capital: float | None = None
    """Run multiple pair stat-arb strategies and aggregate results.

    The class orchestrates running `_run_pair` per pair, scaling equity by
    `per_pair_capital` (or equal split of `capital`) and returns portfolio
    level equity, per-pair results, and a combined performance dict.
    """

    def run(self, prices: pd.DataFrame) -> Dict[str, Any]:
        equity = 0.0
        pair_results = {}
        trades_records = []
        equity_curves = []
        alloc = self.per_pair_capital or (self.capital / len(self.pairs))
        for p in self.pairs:
            if p.x not in prices.columns or p.y not in prices.columns:
                continue
            sub = prices[[p.x, p.y]].dropna(how='any')
            if sub.empty:
                continue
            res = self._run_pair(sub, p)
            # scale pnl by allocation notionally (assuming 1 spread unit ~ alloc)
            scaled_equity = res['equity'] * (alloc / max(res['equity'].abs().max(), 1))
            res_scaled = res.copy()
            res_scaled['scaled_equity'] = scaled_equity
            equity_curves.append(res_scaled['scaled_equity'])
            pair_results[f"{p.x}-{p.y}"] = res_scaled
        if equity_curves:
            combined = pd.concat(equity_curves, axis=1).fillna(method='ffill').sum(axis=1)
            combined.name = 'equity'
            returns = combined.pct_change().fillna(0)
            perf = summarize_performance(combined, returns, pd.DataFrame(trades_records))
        else:
            combined = pd.Series(dtype=float, name='equity')
            returns = pd.Series(dtype=float)
            perf = {}
        return {
            'pair_results': pair_results,
            'portfolio_equity': pd.DataFrame({'equity': combined, 'returns': returns}),
            'performance': perf,
            'trades': pd.DataFrame(trades_records)
        }

    def _run_pair(self, prices: pd.DataFrame, p: PairDefinition) -> pd.DataFrame:
        x = prices[p.x]
        y = prices[p.y]
        beta = hedge_ratio(y, x)
        spread = y - beta * x
        z = _zscore(spread, window=p.lookback)
        long_entry = z < -p.entry_z
        short_entry = z > p.entry_z
        exit_sig = z.abs() < p.exit_z
        position = 0
        pos_list = []
        for i in range(len(z)):
            if position == 0:
                if long_entry.iloc[i]:
                    position = 1
                elif short_entry.iloc[i]:
                    position = -1
            else:
                if exit_sig.iloc[i]:
                    position = 0
            pos_list.append(position)
        df = pd.DataFrame({'spread': spread, 'z': z, 'position': pos_list})
        spread_ret = spread.diff().fillna(0)
        df['pnl'] = df['position'].shift(1).fillna(0) * (-spread_ret)
        df['equity'] = df['pnl'].cumsum()
        return df

__all__ = [
    'PairDefinition', 'MultiPairStatArb'
]
