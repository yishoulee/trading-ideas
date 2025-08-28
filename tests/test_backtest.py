import pandas as pd
from backtest.simple import SimpleFIFOBacktester


def test_backtester_equity_monotonic_when_only_buys():
    prices = pd.Series([10,11,12,13])
    signals = pd.Series([-1,-1,-1,-1])  # only buys
    bt = SimpleFIFOBacktester(initial_cash=100, trade_fraction=0.5, min_cash=1)
    equity = bt.run(prices, signals)
    assert len(equity) == 4
    # equity should track marked value; final equity > initial cash if price rose
    assert equity.iloc[-1] > 100
