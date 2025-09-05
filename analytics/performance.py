from __future__ import annotations
import pandas as pd
import numpy as np

TRADING_DAYS = 252

def sharpe_ratio(returns: pd.Series, risk_free: float = 0.0) -> float:
    """Compute annualized Sharpe ratio from periodic returns.

    Parameters
    - returns: pandas Series of periodic returns (daily).
    - risk_free: annual risk-free rate.

    Returns annualized Sharpe (float). Returns 0.0 for degenerate inputs.
    """
    excess = returns - risk_free / TRADING_DAYS
    vol = excess.std(ddof=0)
    if vol == 0 or np.isnan(vol):
        return 0.0
    return np.sqrt(TRADING_DAYS) * excess.mean() / vol


def cagr(equity: pd.Series) -> float:
    """Compute compound annual growth rate (CAGR) for an equity series.

    Returns 0.0 for empty or non-positive equity series.
    """
    if equity.empty:
        return 0.0
    start = equity.iloc[0]
    end = equity.iloc[-1]
    if start <= 0:
        return 0.0
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    if years <= 0:
        return 0.0
    return (end / start) ** (1/years) - 1


def max_drawdown(equity: pd.Series) -> float:
    """Return the maximum drawdown (most negative peak-to-trough decline).

    Returns 0.0 for empty series.
    """
    if equity.empty:
        return 0.0
    roll_max = equity.cummax()
    dd = equity / roll_max - 1
    return dd.min()


def turnover(trades: pd.DataFrame, equity_series: pd.Series | None = None) -> float:
    """Approximate annualized turnover.

    Parameters
    - trades: DataFrame with columns ['date','notional'] where notional is signed trade size.
    - equity_series: optional equity series used to scale daily notionals.
    """
    if trades.empty:
        return 0.0
    notionals = trades.copy()
    notionals['abs_notional'] = notionals['notional'].abs()
    daily = notionals.groupby('date')['abs_notional'].sum()
    if equity_series is not None and not equity_series.empty:
        equity_align = equity_series.reindex(daily.index).ffill()
        frac = (daily / equity_align).sum()
    else:
        last_equity = equity_series.iloc[-1] if equity_series is not None and not equity_series.empty else notionals['abs_notional'].sum()
        frac = daily.sum() / last_equity
    days = (daily.index[-1] - daily.index[0]).days or 1
    annual_factor = 252 / (days if days > 0 else 1)
    return frac * annual_factor


def summarize_performance(equity: pd.Series, returns: pd.Series, trades: pd.DataFrame | None = None) -> dict:
    return {
        'CAGR': cagr(equity),
        'Sharpe': sharpe_ratio(returns),
        'MaxDrawdown': max_drawdown(equity),
        'Turnover': turnover(trades if trades is not None else pd.DataFrame(columns=['date','notional']), equity)
    }

__all__ = [
    'sharpe_ratio', 'cagr', 'max_drawdown', 'turnover', 'summarize_performance'
]
