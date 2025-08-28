"""Factor library: compute, normalize, and combine cross-sectional factors.

Public API:
 - momentum_factor(prices, lookback)
 - volatility_factor(prices, lookback)
 - zscore(df)
 - composite_rank(factor_dfs, weights)
"""
from .momentum import momentum_factor
from .volatility import volatility_factor
from .core import zscore, composite_rank

__all__ = [
    "momentum_factor",
    "volatility_factor",
    "zscore",
    "composite_rank",
]
