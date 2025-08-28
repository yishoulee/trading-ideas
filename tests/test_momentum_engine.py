import pandas as pd
import numpy as np
from strategies.momentum import MonthlyTopNMomentum, MomentumRebalanceEngine

def test_momentum_engine_trade_log_and_metrics():
    idx = pd.date_range('2023-01-01', periods=260, freq='B')
    data = pd.DataFrame({f'T{i}': (1 + 0.0005*i) ** np.arange(len(idx)) for i in range(8)}, index=idx)
    strat = MonthlyTopNMomentum(n=4, lookback=120)
    engine = MomentumRebalanceEngine(strategy=strat, initial_capital=5000)
    result = engine.run(data)
    assert not result.empty
    assert 'returns' in result.columns and 'drawdown' in result.columns
    # trade log sanity
    assert len(engine.trade_log) > 0
    # equity must remain positive
    assert (result['equity'] > 0).all()
