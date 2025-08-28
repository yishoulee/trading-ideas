from __future__ import annotations
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Iterable, Tuple
from .momentum import MonthlyTopNMomentum, MomentumRebalanceEngine
from analytics.performance import summarize_performance

@dataclass
class ETFFixedUniverseMomentum:
    universe: List[str]
    n: int = 5
    lookback: int = 120

    def to_strategy(self) -> MonthlyTopNMomentum:
        return MonthlyTopNMomentum(n=self.n, lookback=self.lookback)

    def filter_prices(self, prices: pd.DataFrame) -> pd.DataFrame:
        cols = [c for c in self.universe if c in prices.columns]
        return prices[cols]


def run_etf_momentum(prices: pd.DataFrame, config: ETFFixedUniverseMomentum, initial_capital: float = 100_000) -> Dict[str, Any]:
    px = config.filter_prices(prices)
    strat = config.to_strategy()
    engine = MomentumRebalanceEngine(strategy=strat, initial_capital=initial_capital)
    result = engine.run(px)
    perf = summarize_performance(result['equity'], result['returns'], pd.DataFrame(engine.trade_log))
    return {
        'config': config,
        'equity_curve': result,
        'performance': perf,
        'trades': pd.DataFrame(engine.trade_log)
    }


def parameter_grid(param_dict: Dict[str, Iterable]) -> List[Dict[str, Any]]:
    from itertools import product
    keys = list(param_dict.keys())
    grids = []
    for combo in product(*param_dict.values()):
        grids.append({k: v for k, v in zip(keys, combo)})
    return grids


def optimize_etf_momentum(prices: pd.DataFrame, universe: List[str], param_space: Dict[str, Iterable], top_k: int = 5, initial_capital: float = 100_000) -> pd.DataFrame:
    rows = []
    for params in parameter_grid(param_space):
        cfg = ETFFixedUniverseMomentum(universe=universe, n=params['n'], lookback=params['lookback'])
        out = run_etf_momentum(prices, cfg, initial_capital=initial_capital)
        perf = out['performance']
        rows.append({
            'n': params['n'],
            'lookback': params['lookback'],
            'CAGR': perf['CAGR'],
            'Sharpe': perf['Sharpe'],
            'MaxDrawdown': perf['MaxDrawdown'],
            'Turnover': perf['Turnover']
        })
    df = pd.DataFrame(rows)
    df = df.sort_values(by=['Sharpe','CAGR'], ascending=False).head(top_k)
    return df.reset_index(drop=True)

__all__ = [
    'ETFFixedUniverseMomentum', 'run_etf_momentum', 'optimize_etf_momentum'
]
