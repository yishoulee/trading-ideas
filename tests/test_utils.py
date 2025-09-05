import pandas as pd
import numpy as np
from utils import zscore, rolling_beta, parameter_grid


def test_zscore_global_series():
    s = pd.Series([1.0, 2.0, 3.0, 4.0])
    z = zscore(s)
    assert np.isclose(z.mean(), 0)
    assert np.isclose(z.std(ddof=0), 1)


def test_zscore_global_constant():
    s = pd.Series([5.0, 5.0, 5.0])
    z = zscore(s)
    assert (z == 0).all()


def test_zscore_rolling_series():
    s = pd.Series(range(10), dtype=float)
    z = zscore(s, window=3)
    # first two will be 0 due to min_periods default turning NaN to 0
    assert len(z) == len(s)
    assert z.isna().sum() == 0


def test_rolling_beta():
    x = pd.Series(np.arange(100).astype(float))
    y = 2 * x + np.random.normal(0, 0.1, size=len(x))
    rb = rolling_beta(x, y, window=20)
    assert len(rb) == len(x)
    assert rb.isna().sum() >= 19


def test_parameter_grid():
    grid = parameter_grid({'a': [1, 2], 'b': ['x']})
    assert isinstance(grid, list)
    assert len(grid) == 2
    assert all('a' in g and 'b' in g for g in grid)
