import pandas as pd
import numpy as np
from factors import value_factor, quality_factor, size_factor, composite_rank


def _make_prices(rows: int = 70):
    idx = pd.date_range('2024-01-01', periods=rows, freq='B')
    base = np.linspace(50, 60, rows)
    prices = pd.DataFrame({
        'LOW': base * 0.5,              # lowest price
        'MID': base,                    # mid price
        'HIGH': base * 2.0,             # highest price
        'STABLE': np.full(rows, 100.0), # constant -> zero vol
        'NOISY': 100 + np.cumsum(np.random.randn(rows)) * 0.5, # higher vol
    }, index=idx)
    return prices


def test_value_factor_inverse_relationship():
    prices = _make_prices()
    val = value_factor(prices)
    last = prices.iloc[-1]
    # Smallest price should have largest value score (inverse relationship)
    assert val.sort_values(ascending=False).index[0] == last.sort_values().index[0]
    # Largest price should have smallest value score
    assert val.sort_values().index[0] == last.sort_values(ascending=False).index[0]


def test_size_factor_smaller_price_higher_score():
    prices = _make_prices()
    size = size_factor(prices)
    avg = prices.tail(63).mean()
    assert size.sort_values(ascending=False).index[0] == avg.sort_values().index[0]


def test_quality_factor_lower_vol_higher_score():
    prices = _make_prices()
    q = quality_factor(prices)
    assert q['STABLE'] > q['NOISY']


def test_composite_with_new_factors():
    prices = _make_prices()
    factors = {
        'value': value_factor(prices),
        'quality': quality_factor(prices),
        'size': size_factor(prices)
    }
    weights = {'value': 0.4, 'quality': 0.3, 'size': 0.3}
    comp = composite_rank(factors, weights)
    assert not comp.empty
    assert set(comp.index) == set(prices.columns)
