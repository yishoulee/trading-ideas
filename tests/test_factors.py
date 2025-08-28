import pandas as pd
import numpy as np
from factors import momentum_factor, volatility_factor, composite_rank

def test_factor_composite_rank():
    idx = pd.date_range('2023-01-01', periods=300, freq='B')
    prices = pd.DataFrame({f'A{i}': (1 + 0.0005*i) ** np.arange(len(idx)) for i in range(1,6)}, index=idx)
    mom = momentum_factor(prices, lookback=120)
    vol = volatility_factor(prices, lookback=120)
    comp = composite_rank({'mom': mom, 'vol': vol}, {'mom': 0.6, 'vol': 0.4})
    assert not comp.empty
    assert comp.index.isin(prices.columns).all()
