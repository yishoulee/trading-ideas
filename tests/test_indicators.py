import pandas as pd
from indicators import bollinger_bands, stochastic_oscillator


def test_bollinger_shapes():
    s = pd.Series([1,2,3,4,5,6,7,8,9,10])
    out = bollinger_bands(s, window=3)
    assert set(out.columns) == {"sma", "upper", "lower"}
    assert len(out) == len(s)


def test_stochastic_columns():
    df = pd.DataFrame({"High": [1,2,3,4,5], "Low": [0,1,1,2,2], "Close": [0.5,1.5,2.5,3.5,4.5]})
    out = stochastic_oscillator(df, k_period=2, d_period=2)
    assert set(out.columns) == {"k", "d"}
    assert len(out) == len(df)
