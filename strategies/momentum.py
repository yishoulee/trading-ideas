from __future__ import annotations
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any


def trailing_return(prices: pd.DataFrame, start_idx: int, end_idx: int) -> pd.Series:
    start = prices.iloc[start_idx]
    end = prices.iloc[end_idx]
    return end / start - 1

@dataclass
class MonthlyTopNMomentum:
    n: int = 10
    lookback: int = 252  # max trading days (~1y)

    def select(self, prices: pd.DataFrame, pos: int) -> list[str]:
        if pos == 0:
            return []
        trailing = min(self.lookback, pos)
        tr = trailing_return(prices, pos - trailing, pos)
        tr = tr.replace([np.inf, -np.inf], np.nan).dropna()
        return tr.sort_values(ascending=False).head(self.n).index.tolist()


@dataclass
class MomentumRebalanceEngine:
    strategy: MonthlyTopNMomentum
    initial_capital: float = 10_000
    trade_log: List[Dict[str, Any]] = field(default_factory=list)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def run(self, prices: pd.DataFrame) -> pd.DataFrame:
        prices = prices.sort_index()
        rebalance_points = prices.resample('MS').first().index
        equity = self.initial_capital
        prev_holdings: Dict[str, float] = {}
        for i, date in enumerate(rebalance_points):
            pos_arr = prices.index.get_indexer([date], method='nearest')
            pos = pos_arr[0]
            if pos <= 0:
                continue
            # Actual trading date corresponding to this rebalance
            actual_date = prices.index[pos]
            tickers = self.strategy.select(prices, pos)
            if not tickers:
                continue
            allocation = equity / len(tickers)
            # Determine next rebalance calendar date and map to trading index
            cal_next = rebalance_points[i+1] if i < len(rebalance_points)-1 else prices.index[-1]
            next_pos_arr = prices.index.get_indexer([cal_next], method='nearest')
            next_pos = next_pos_arr[0]
            actual_next = prices.index[next_pos]
            start_prices = prices.loc[actual_date, tickers]
            # target shares
            target_shares = {t: allocation / start_prices[t] for t in tickers}
            # derive trades vs prev holdings (shares)
            trades = {}
            for t in tickers:
                prev = prev_holdings.get(t, 0)
                delta = target_shares[t] - prev
                if abs(delta) > 1e-9:
                    trades[t] = delta
            for t in list(prev_holdings.keys()):
                if t not in tickers and prev_holdings[t] != 0:
                    trades[t] = -prev_holdings[t]
            # log trades
            for t, sh in trades.items():
                self.trade_log.append({
                    'date': date,
                    'ticker': t,
                    'shares': sh,
                    'price': start_prices.get(t, np.nan),
                    'notional': sh * start_prices.get(t, np.nan)
                })
            # evolve portfolio to next rebalance
            period_slice = prices.loc[actual_date:actual_next, tickers].ffill()
            if period_slice.empty:
                continue
            end_prices = period_slice.iloc[-1]
            equity = sum(target_shares[t] * end_prices[t] for t in tickers)
            prev_holdings = target_shares
            self.history.append({'date': actual_next, 'equity': equity, 'holdings': tickers})
        df = pd.DataFrame(self.history).set_index('date')
        if not df.empty:
            df['returns'] = df['equity'].pct_change().fillna(0)
            cummax = df['equity'].cummax()
            df['drawdown'] = df['equity']/cummax - 1
        return df


def run_monthly_rebalance(prices: pd.DataFrame, strategy: MonthlyTopNMomentum, initial_capital: float = 10_000) -> pd.DataFrame:
    """Backward compatible wrapper using new engine."""
    engine = MomentumRebalanceEngine(strategy=strategy, initial_capital=initial_capital)
    return engine.run(prices)
