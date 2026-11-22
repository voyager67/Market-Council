"""Small, event-time-aware OHLCV backtester for transparent strategy research.

Signals observe completed bars and execute at the following bar's open. This is
intentionally a research engine, not a broker simulator or proof of edge.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import asdict, dataclass
from typing import Protocol

from .models import Bar


class Strategy(Protocol):
    name: str

    def target_exposure(self, history: list[Bar]) -> float: ...


@dataclass(frozen=True, slots=True)
class BacktestConfig:
    initial_equity: float = 100_000.0
    commission_bps: float = 5.0
    slippage_bps: float = 5.0
    bars_per_year: int | None = None
    allow_short: bool = False

    def validate(self) -> None:
        numbers = (self.initial_equity, self.commission_bps, self.slippage_bps)
        if not all(math.isfinite(value) for value in numbers):
            raise ValueError("backtest numeric configuration must be finite")
        if self.initial_equity <= 0 or self.commission_bps < 0 or self.slippage_bps < 0:
            raise ValueError("initial equity must be positive and costs cannot be negative")
        if self.commission_bps + self.slippage_bps >= 5_000:
            raise ValueError("combined commission and slippage must be below 5,000 bps")
        if self.bars_per_year is not None and self.bars_per_year <= 0:
            raise ValueError("bars_per_year must be positive")


@dataclass(frozen=True, slots=True)
class BacktestFill:
    timestamp: str
    side: str
    exposure_before: float
    exposure_after: float
    reference_price: float
    estimated_cost: float


@dataclass(frozen=True, slots=True)
class BacktestResult:
    strategy: str
    observations: int
    initial_equity: float
    final_equity: float
    total_return_pct: float
    annualised_return_pct: float | None
    annualised_sharpe: float | None
    max_drawdown_pct: float
    exposure_pct: float
    turnover: float
    fills: tuple[BacktestFill, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict:
        result = asdict(self)
        result["fills"] = [asdict(fill) for fill in self.fills]
        result["warnings"] = list(self.warnings)
        return result


class SmaCrossStrategy:
    """Long/cash SMA cross; the signal is only used at the next bar's open."""

    name = "sma-cross"

    def __init__(self, fast: int = 10, slow: int = 30) -> None:
        if fast < 2 or slow <= fast:
            raise ValueError("require 2 <= fast < slow")
        self.fast = fast
        self.slow = slow

    def target_exposure(self, history: list[Bar]) -> float:
        if len(history) < self.slow:
            return 0.0
        closes = [bar.close for bar in history]
        fast_sma = sum(closes[-self.fast :]) / self.fast
        slow_sma = sum(closes[-self.slow :]) / self.slow
        return 1.0 if fast_sma > slow_sma else 0.0


def run_backtest(bars: list[Bar], strategy: Strategy, config: BacktestConfig | None = None) -> BacktestResult:
    config = config or BacktestConfig()
    config.validate()
    if len(bars) < 3:
        raise ValueError("at least three bars are required")
    for bar in bars:
        values = (bar.open, bar.high, bar.low, bar.close, bar.volume)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("bars must contain finite OHLCV values")
        if min(bar.open, bar.high, bar.low, bar.close) <= 0 or bar.volume < 0:
            raise ValueError("bars require positive prices and non-negative volume")
        if bar.high < max(bar.open, bar.close, bar.low) or bar.low > min(bar.open, bar.close, bar.high):
            raise ValueError("bars contain inconsistent OHLC bounds")
        if bar.timestamp.tzinfo is None or bar.timestamp.utcoffset() is None:
            raise ValueError("bar timestamps must be timezone-aware")
    for previous, current in zip(bars, bars[1:]):
        if current.timestamp <= previous.timestamp:
            raise ValueError("bars must be strictly ascending")
    if not getattr(strategy, "name", None):
        raise ValueError("strategy must have a stable name")

    equity = config.initial_equity
    peak = equity
    max_dd = 0.0
    exposure = 0.0
    equity_returns: list[float] = []
    fills: list[BacktestFill] = []
    turnover = 0.0
    active_bars = 0

    for index in range(len(bars) - 1):
        signal_bar = bars[index]
        next_bar = bars[index + 1]
        target = float(strategy.target_exposure(bars[: index + 1]))
        if not math.isfinite(target) or abs(target) > 1:
            raise ValueError("strategy exposure must be finite and between -1 and 1")
        if target < 0 and not config.allow_short:
            raise ValueError("strategy requested short exposure but allow_short is false")

        equity_before = equity
        # Existing exposure carries the close-to-next-open gap.
        overnight_return = next_bar.open / signal_bar.close - 1.0
        equity *= 1.0 + exposure * overnight_return
        if not math.isfinite(equity) or equity <= 0:
            raise ValueError("backtest equity depleted during the overnight gap; margin and liquidation are not modelled")

        delta = target - exposure
        if delta:
            cost = equity * abs(delta) * (config.commission_bps + config.slippage_bps) / 10_000
            equity -= cost
            turnover += abs(delta)
            fills.append(BacktestFill(
                timestamp=next_bar.timestamp.isoformat(),
                side="BUY" if delta > 0 else "SELL",
                exposure_before=exposure,
                exposure_after=target,
                reference_price=next_bar.open,
                estimated_cost=cost,
            ))
        exposure = target

        # New exposure participates only after the next-open execution.
        intraday_return = next_bar.close / next_bar.open - 1.0
        equity *= 1.0 + exposure * intraday_return
        if not math.isfinite(equity) or equity <= 0:
            raise ValueError("backtest equity depleted during the bar; margin and liquidation are not modelled")
        if exposure:
            active_bars += 1
        peak = max(peak, equity)
        max_dd = min(max_dd, equity / peak - 1.0)
        equity_returns.append(equity / equity_before - 1.0)

    # Mark the open position closed at the final close so reported equity is flat/cash.
    if exposure:
        final_bar = bars[-1]
        close_cost = equity * abs(exposure) * (config.commission_bps + config.slippage_bps) / 10_000
        equity -= close_cost
        peak = max(peak, equity)
        max_dd = min(max_dd, equity / peak - 1.0)
        turnover += abs(exposure)
        fills.append(BacktestFill(
            timestamp=final_bar.timestamp.isoformat(), side="SELL" if exposure > 0 else "BUY_TO_COVER",
            exposure_before=exposure, exposure_after=0.0,
            reference_price=final_bar.close, estimated_cost=close_cost,
        ))
        exposure = 0.0

    total_return = equity / config.initial_equity - 1.0
    elapsed_years = len(equity_returns) / config.bars_per_year if config.bars_per_year else None
    annualised = ((equity / config.initial_equity) ** (1 / elapsed_years) - 1) * 100 if elapsed_years and equity > 0 else None
    sharpe = None
    if config.bars_per_year and len(equity_returns) >= 2:
        deviation = statistics.stdev(equity_returns)
        if deviation > 0:
            sharpe = statistics.mean(equity_returns) / deviation * math.sqrt(config.bars_per_year)
    warnings = ["Signals are evaluated on completed bars and filled at the next bar open."]
    warnings.append("Fees and slippage are simple bps estimates; spread, impact, funding, borrow, taxes, and partial fills are not modelled.")
    warnings.append("No survivorship, delisting, corporate-action, or point-in-time universe correction is performed.")
    if config.bars_per_year is None:
        warnings.append("Annualised return and Sharpe omitted: supply a timeframe-appropriate bars_per_year.")
    return BacktestResult(
        strategy=strategy.name, observations=len(bars) - 1,
        initial_equity=config.initial_equity, final_equity=equity,
        total_return_pct=total_return * 100, annualised_return_pct=annualised,
        annualised_sharpe=sharpe, max_drawdown_pct=max_dd * 100,
        exposure_pct=active_bars / max(1, len(equity_returns)) * 100,
        turnover=turnover, fills=tuple(fills), warnings=tuple(warnings),
    )
