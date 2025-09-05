import pandas as pd
import numpy as np

# Placeholder value factor: inverse of price (proxy for cheapness when fundamentals absent)
def value_factor(prices: pd.DataFrame) -> pd.Series:
    """Value factor proxy: inverse of last price as a cheapness measure.

    This is a placeholder where lower-priced assets receive higher scores.
    """
    last = prices.iloc[-1]
    with np.errstate(divide='ignore'):
        val = 1 / last.replace(0, np.nan)
    return val.replace([np.inf, -np.inf], np.nan)

__all__ = ['value_factor']
