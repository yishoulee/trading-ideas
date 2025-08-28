import pandas as pd
import numpy as np

# Placeholder size factor: assume column names include market cap ordering or proxy by average dollar price *not implemented*
# For demo we use average price (lower price treated as smaller size => size factor returns negative avg price so large negative = large cap)

def size_factor(prices: pd.DataFrame) -> pd.Series:
    avg_price = prices.tail(63).mean() if prices.shape[0] >= 63 else prices.mean()
    # Return negative so that smaller average price => higher factor (treating small-cap preference) 
    return (-avg_price).replace([np.inf, -np.inf], np.nan)

__all__ = ['size_factor']
