from __future__ import annotations
from typing import Optional

import pandas as pd
import numpy as np


def zscore(data: pd.Series | pd.DataFrame,
            window: Optional[int] = None,
            ddof: int = 0,
            min_periods: Optional[int] = None,
            axis: int = 0) -> pd.Series | pd.DataFrame:
    """Compute z-score normalization for Series or DataFrame.

    See `utils.zscore` docstring in previous layout.
    """

    is_series = isinstance(data, pd.Series)

    if is_series:
        s = data
        if window is None:
            mu = s.mean()
            sigma = s.std(ddof=ddof)
            if sigma == 0 or (isinstance(sigma, float) and np.isclose(sigma, 0)):
                return pd.Series(0, index=s.index)
            return (s - mu) / sigma
        # rolling
        rol_mean = s.rolling(window=window, min_periods=min_periods).mean()
        rol_std = s.rolling(window=window, min_periods=min_periods).std(ddof=ddof)
        out = (s - rol_mean) / rol_std
        out = out.fillna(0).replace([np.inf, -np.inf], 0)
        return out

    df = data
    if window is None:
        mu = df.mean(axis=axis)
        sigma = df.std(axis=axis, ddof=ddof)
        sigma_replaced = sigma.replace({0: np.nan})
        out = (df - mu) / sigma_replaced
        out = out.fillna(0)
        return out

    if axis == 0:
        rol_mean = df.rolling(window=window, min_periods=min_periods).mean()
        rol_std = df.rolling(window=window, min_periods=min_periods).std(ddof=ddof)
    else:
        rol_mean = df.T.rolling(window=window, min_periods=min_periods).mean().T
        rol_std = df.T.rolling(window=window, min_periods=min_periods).std(ddof=ddof).T

    out = (df - rol_mean) / rol_std
    out = out.fillna(0).replace([np.inf, -np.inf], 0)
    return out


def rolling_beta(x: pd.Series, y: pd.Series, window: int = 60) -> pd.Series:
    """Estimate rolling beta of y ~ x using simple OLS per window."""
    betas: list[float] = []
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
