import pandas as pd
import numpy as np
from strategies.momentum import MonthlyTopNMomentum, run_monthly_rebalance

def test_momentum_strategy_basic():
    # fabricate price panel for 6 tickers over 300 days with trending differences
    idx = pd.date_range('2023-01-01', periods=300, freq='B')
    steps = np.arange(300)
    data = pd.DataFrame({f'T{i}': (1 + 0.001*i) ** steps for i in range(6)}, index=idx)
    strat = MonthlyTopNMomentum(n=3, lookback=60)
    result = run_monthly_rebalance(data, strat, initial_capital=1000)
    assert not result.empty
    assert (result['equity'] > 0).all()
    # Ensure holdings length equals n mostly
    assert result['holdings'].apply(len).median() == 3
