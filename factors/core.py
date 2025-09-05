import pandas as pd
from typing import Dict, List

from utils import zscore as _zscore

def zscore(series: pd.Series) -> pd.Series:
    """Backwards-compatible thin wrapper around `utils.zscore`.

    The project's factor API historically exposed `zscore(series)` which
    computes the global (full-series) z-score. Keep that signature here
    and delegate to the generalized implementation in `utils`.
    """
    return _zscore(series, window=None)

def composite_rank(factors: Dict[str, pd.Series], weights: Dict[str, float]) -> pd.Series:
    """Combine multiple factor score Series via weighted z-scored sum.
    Missing values are ignored per factor.
    """
    aligned = pd.DataFrame({k: v for k,v in factors.items()})
    zed = aligned.apply(lambda col: _zscore(col, window=None))
    w = pd.Series(weights)
    w = w / w.sum()
    composite = (zed * w).sum(axis=1)
    return composite.sort_values(ascending=False)

