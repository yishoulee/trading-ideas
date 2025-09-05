"""Project-wide utilities package.

Expose small reusable helpers used throughout the project:
- `zscore`: global and rolling z-score normalization
- `rolling_beta`: rolling regression beta estimator
- `parameter_grid`: grid search helper

Import like: from utils import zscore
"""
from .stats import zscore
from .stats import rolling_beta
from .grid import parameter_grid

__all__ = ["zscore", "rolling_beta", "parameter_grid"]
