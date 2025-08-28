from __future__ import annotations
import pandas as pd
from dataclasses import dataclass, field


@dataclass
class Trade:
    entry_price: float
    size: float  # quantity of asset


@dataclass
class SimpleFIFOBacktester:
    initial_cash: float = 100.0
    trade_fraction: float = 0.25  # fraction of available cash to deploy per buy
    min_cash: float = 10.0
    open_trades: list[Trade] = field(default_factory=list)
    cash: float = None

    def __post_init__(self):
        self.cash = self.initial_cash

    def step(self, price: float, signal: int):
        # signal: 1 = sell (reduce), -1 = buy (add)
        if signal == -1 and self.cash > self.min_cash:
            to_deploy = self.cash * self.trade_fraction
            size = to_deploy / price
            self.cash -= to_deploy
            self.open_trades.append(Trade(entry_price=price, size=size))
        elif signal == 1 and self.open_trades:
            trade = self.open_trades.pop(0)
            proceeds = trade.size * price
            self.cash += proceeds

    def mark_to_market(self, price: float) -> float:
        exposure = sum(t.size for t in self.open_trades) * price
        return self.cash + exposure

    def run(self, prices: pd.Series, signals: pd.Series) -> pd.Series:
        equity_curve = []
        for price, signal in zip(prices, signals):
            self.step(price, signal)
            equity_curve.append(self.mark_to_market(price))
        return pd.Series(equity_curve, index=prices.index, name="equity")
