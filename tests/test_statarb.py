import pandas as pd
import numpy as np
from strategies.statarb import PairStatArb


def test_pair_statarb_signals():
    # create synthetic cointegrated-like series: y = 2*x + noise
    idx = pd.date_range('2024-01-01', periods=200, freq='B')
    x = np.cumsum(np.random.randn(len(idx))) + 100
    noise = np.random.randn(len(idx)) * 0.5
    y = 2 * x + noise
    prices = pd.DataFrame({'X': x, 'Y': y}, index=idx)
    strat = PairStatArb(x_symbol='X', y_symbol='Y', lookback=20, entry_z=1.5, exit_z=0.2)
    res = strat.backtest(prices)
    assert 'position' in res.columns
    assert res['position'].abs().max() <= 1
    assert res['equity'].iloc[-1] == res['pnl'].cumsum().iloc[-1]
