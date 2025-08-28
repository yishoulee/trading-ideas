import pandas as pd
import numpy as np

# Placeholder quality factor: stability of returns (lower volatility => higher quality)
# Implemented as negative rolling std of returns across last 63 trading days (~quarter)
def quality_factor(prices: pd.DataFrame, lookback: int = 63) -> pd.Series:
    if prices.shape[0] < lookback + 2:
        lookback = prices.shape[0] - 2
    rets = prices.pct_change().iloc[-lookback:]
    vol = rets.std()
    return (-vol).replace([np.inf, -np.inf], np.nan)

__all__ = ['quality_factor']
