import pandas as pd
import numpy as np

def momentum_factor(prices: pd.DataFrame, lookback: int = 252) -> pd.Series:
    """Compute simple price momentum: return over lookback window.
    Returns a cross-sectional Series for the last available date.
    """
    if prices.shape[0] < lookback + 1:
        lookback = prices.shape[0] - 1
    returns = prices.iloc[-1] / prices.iloc[-lookback-1] - 1
    return returns.replace([np.inf, -np.inf], np.nan)
