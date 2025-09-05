import pandas as pd

def bollinger_bands(close: pd.Series, window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
    """Compute Bollinger Bands (SMA +/- num_std * STD).

    Parameters
    - close: price series
    - window: lookback window for SMA/std
    - num_std: number of standard deviations for upper/lower bands

    Returns DataFrame with columns: 'sma', 'upper', 'lower'.
    """
    sma = close.rolling(window).mean()
    std = close.rolling(window).std(ddof=0)
    upper = sma + num_std * std
    lower = sma - num_std * std
    return pd.DataFrame({"sma": sma, "upper": upper, "lower": lower})


def stochastic_oscillator(df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> pd.DataFrame:
    """Compute Stochastic Oscillator %K and %D.

    Expects columns High, Low, Close.
    Returns DataFrame with columns: k, d.
    """
    n_high = df['High'].rolling(k_period).max()
    n_low = df['Low'].rolling(k_period).min()
    k = (df['Close'] - n_low) / (n_high - n_low)
    d = k.rolling(d_period).mean()
    out = pd.DataFrame({'k': k.fillna(0), 'd': d.fillna(0)})
    return out
    k = (df['Close'] - n_low) * 100 / (n_high - n_low)
    d = k.rolling(d_period).mean()
    return pd.DataFrame({"k": k, "d": d})

__all__ = ["bollinger_bands", "stochastic_oscillator"]
