import pandas as pd
import numpy as np
from typing import Dict, List

def zscore(series: pd.Series) -> pd.Series:
    mu = series.mean()
    sigma = series.std(ddof=0)
    return (series - mu) / sigma if sigma and not np.isclose(sigma,0) else series * 0


def composite_rank(factors: Dict[str, pd.Series], weights: Dict[str, float]) -> pd.Series:
    """Combine multiple factor score Series via weighted z-scored sum.
    Missing values are ignored per factor.
    """
    aligned = pd.DataFrame({k: v for k,v in factors.items()})
    zed = aligned.apply(zscore)
    w = pd.Series(weights)
    w = w / w.sum()
    composite = (zed * w).sum(axis=1)
    return composite.sort_values(ascending=False)
