from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

import pandas as pd


@dataclass
class Trade:
    """Simple trade record for a filled buy order.

    Attributes:
        entry_price: Price at which the trade was opened.
        size: Quantity purchased.
    """

    entry_price: float
    size: float


@dataclass
class SimpleFIFOBacktester:
    """Very small FIFO backtester used by unit tests.

    Behavior:
    - On signal == -1, buys using `trade_fraction` of available cash (if above `min_cash`).
    - On signal == 1, sells the earliest opened trade (FIFO) and realizes P&L.
    - Commission and slippage are applied as basis points of notional.

    The backtester stores `open_trades`, `cash`, and `cost_paid` for inspection.
    """

    initial_cash: float = 100.0
    trade_fraction: float = 0.25
    min_cash: float = 10.0
    commission_bps: float = 0.0
    slippage_bps: float = 0.0
    open_trades: List[Trade] = field(default_factory=list)
    cash: float | None = None
    cost_paid: float = 0.0

    def __post_init__(self) -> None:
        """Initialize runtime state."""
        self.cash = float(self.initial_cash)

    def step(self, price: float, signal: int) -> None:
        """Execute one-step of trading given a market price and signal.

        Signals:
        -1 -> buy (allocate fraction of cash)
         1 -> sell (close earliest open trade)
        0 -> hold
        """
        if signal == -1 and self.cash is not None and self.cash > self.min_cash:
            to_deploy = self.cash * self.trade_fraction
            if to_deploy <= 0:
                return
            size = to_deploy / price
            notional = to_deploy
            cost = notional * (self.commission_bps + self.slippage_bps) / 10_000
            self.cash -= (to_deploy + cost)
            self.cost_paid += cost
            self.open_trades.append(Trade(entry_price=price, size=size))

        elif signal == 1 and self.open_trades:
            trade = self.open_trades.pop(0)
            proceeds = trade.size * price
            cost = proceeds * (self.commission_bps + self.slippage_bps) / 10_000
            self.cash += (proceeds - cost)
            self.cost_paid += cost

    def mark_to_market(self, price: float) -> float:
        """Return mark-to-market equity (cash + current exposure)."""
        exposure = sum(t.size for t in self.open_trades) * price
        return float((self.cash or 0.0) + exposure)

    def run(self, prices: pd.Series, signals: pd.Series) -> pd.Series:
        """Run the backtester over a sequence of prices and signals.

        Returns a pandas Series of equity values indexed like `prices`.
        """
        equity_curve: list[float] = []
        for price, signal in zip(prices, signals):
            self.step(price, signal)
            equity_curve.append(self.mark_to_market(price))
        return pd.Series(equity_curve, index=prices.index, name="equity")
