import pandas as pd
from backtest.simple import SimpleFIFOBacktester


def test_transaction_costs_reduce_equity():
    prices = pd.Series([10, 11, 12, 13, 14])
    # alternating buy signals ensure multiple trades
    signals = pd.Series([-1, 0, -1, 0, 1])
    bt_no_cost = SimpleFIFOBacktester(initial_cash=1000, trade_fraction=0.5, min_cash=1,
                                      commission_bps=0, slippage_bps=0)
    equity_no_cost = bt_no_cost.run(prices, signals)

    bt_cost = SimpleFIFOBacktester(initial_cash=1000, trade_fraction=0.5, min_cash=1,
                                   commission_bps=25, slippage_bps=10)  # 35 bps each side
    equity_cost = bt_cost.run(prices, signals)

    assert equity_cost.iloc[-1] <= equity_no_cost.iloc[-1]
    assert bt_cost.cost_paid > 0
    assert abs(bt_no_cost.cost_paid) < 1e-9
