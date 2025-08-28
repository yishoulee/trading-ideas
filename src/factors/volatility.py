import pandas as pd
import numpy as np

def volatility_factor(prices: pd.DataFrame, lookback: int = 252) -> pd.Series:
    """Compute (negative) realized volatility over lookback (higher vol => lower score).
    We return -stdev of daily returns so that higher is better (low vol preference).
    """
    if prices.shape[0] < lookback + 2:
        lookback = prices.shape[0] - 2
    rets = prices.pct_change().iloc[-lookback:]
    vol = rets.std()
    return (-vol).replace([np.inf, -np.inf], np.nan)
