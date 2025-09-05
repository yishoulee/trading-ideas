from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict, Iterable, List

def parameter_grid(param_dict: Dict[str, Iterable]):
    """Create a list of parameter dicts from param grid.

    Example: parameter_grid({'n':[2,3], 'lookback':[60,120]})
    """
    from itertools import product
    keys = list(param_dict.keys())
    grids = []
    for combo in product(*param_dict.values()):
        grids.append({k: v for k, v in zip(keys, combo)})
    return grids


def zscore(series: pd.Series, window: int = 20) -> pd.Series:
    """Rolling z-score with NaN handling."""
    rol_mean = series.rolling(window).mean()
    rol_std = series.rolling(window).std()
    return (series - rol_mean) / rol_std


def rolling_beta(x: pd.Series, y: pd.Series, window: int = 60) -> pd.Series:
    """Estimate rolling beta of y ~ x using simple OLS per window."""
    betas: List[float] = []
    idx = x.index
    for i in range(window, len(x) + 1):
        xx = x.iloc[i - window:i].values
        yy = y.iloc[i - window:i].values
        if np.all(np.isfinite(xx)) and np.all(np.isfinite(yy)):
            beta = np.polyfit(xx, yy, 1)[0]
        else:
            beta = np.nan
        betas.append(beta)
    return pd.Series([np.nan] * (window - 1) + betas, index=idx)


def monthly_returns_heatmap(prices: pd.DataFrame) -> pd.DataFrame:
    """Return monthly returns pivot table (tickers x months)."""
    monthly = prices.resample('M').last().pct_change()
    monthly.index = monthly.index.to_period('M')
    return monthly
