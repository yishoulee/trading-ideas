from __future__ import annotations
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Callable, List, Any
from factors import momentum_factor, volatility_factor, composite_rank
from analytics.performance import summarize_performance

FactorFunc = Callable[[pd.DataFrame], pd.Series]

DEFAULT_FACTORS: Dict[str, FactorFunc] = {
    'momentum': lambda px: momentum_factor(px, lookback=126),
    'low_vol': lambda px: volatility_factor(px, lookback=126),
}

@dataclass
class FactorConfig:
    weights: Dict[str, float]
    top_n: int = 20
    rebalance_freq: str = 'M'  # monthly end
    long_short: bool = False
    short_fraction: float = 0.0  # fraction of long notional to allocate to shorts

@dataclass
class FactorPortfolioEngine:
    factor_funcs: Dict[str, FactorFunc] = field(default_factory=lambda: DEFAULT_FACTORS)
    config: FactorConfig = field(default_factory=lambda: FactorConfig(weights={'momentum':0.6,'low_vol':0.4}))
    initial_capital: float = 1_000_000

    def run(self, prices: pd.DataFrame) -> Dict[str, Any]:
        prices = prices.sort_index()
        rebal_dates = prices.resample(self._freq_to_rule()).last().index
        capital = self.initial_capital
        positions: Dict[str, float] = {}
        history = []
        trade_log = []
        prev_equity_series = []
        for d in rebal_dates:
            if d not in prices.index:
                # align to nearest previous trading day
                locs = prices.index.get_indexer([d], method='nearest')
                d = prices.index[locs[0]]
            window_px = prices.loc[:d]
            if len(window_px) < 30:
                continue
            factor_scores = {name: f(window_px) for name, f in self.factor_funcs.items() if name in self.config.weights}
            composite = composite_rank(factor_scores, self.config.weights)
            if composite.empty:
                continue
            longs = composite.head(self.config.top_n).index.tolist()
            shorts: List[str] = []
            if self.config.long_short and self.config.short_fraction > 0:
                shorts = composite.tail(self.config.top_n).index.tolist()
            target_long_notional = capital
            target_short_notional = capital * self.config.short_fraction if shorts else 0
            per_long = target_long_notional / len(longs) if longs else 0
            per_short = target_short_notional / len(shorts) if shorts else 0
            prices_d = prices.loc[d]
            target_positions: Dict[str, float] = {}
            for sym in longs:
                target_positions[sym] = per_long / prices_d.get(sym, np.nan)
            for sym in shorts:
                target_positions[sym] = - per_short / prices_d.get(sym, np.nan)
            # record trades
            all_syms = set(positions) | set(target_positions)
            for sym in all_syms:
                prev = positions.get(sym, 0.0)
                new = target_positions.get(sym, 0.0)
                delta = new - prev
                if abs(delta) > 1e-9:
                    trade_log.append({'date': d, 'symbol': sym, 'shares': delta, 'price': prices_d.get(sym, np.nan), 'notional': delta * prices_d.get(sym, np.nan)})
            positions = target_positions
            # compute equity until next rebalance
            next_idx = list(rebal_dates).index(d) + 1
            end_date = rebal_dates[next_idx] if next_idx < len(rebal_dates) else prices.index[-1]
            segment = prices.loc[d:end_date]
            # mark to market each day
            for day, row in segment.iterrows():
                equity_day = sum(shares * row.get(sym, np.nan) for sym, shares in positions.items())
                prev_equity_series.append({'date': day, 'equity': equity_day})
            capital = prev_equity_series[-1]['equity'] if prev_equity_series else capital
        equity_df = pd.DataFrame(prev_equity_series).drop_duplicates('date').set_index('date').sort_index()
        if not equity_df.empty:
            equity_df['returns'] = equity_df['equity'].pct_change().fillna(0)
            equity_df['drawdown'] = equity_df['equity'] / equity_df['equity'].cummax() - 1
        perf = summarize_performance(equity_df['equity'] if 'equity' in equity_df else pd.Series(dtype=float), equity_df['returns'] if 'returns' in equity_df else pd.Series(dtype=float), pd.DataFrame(trade_log))
        return {
            'equity': equity_df,
            'performance': perf,
            'trades': pd.DataFrame(trade_log),
        }

    def _freq_to_rule(self) -> str:
        if self.config.rebalance_freq.upper() in ('M','MS'):
            return 'M'
        if self.config.rebalance_freq.upper() in ('W','W-FRI'):
            return 'W-FRI'
        return 'M'

__all__ = [
    'FactorConfig', 'FactorPortfolioEngine'
]
