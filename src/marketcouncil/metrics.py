"""Transparent descriptive metrics; no prediction or signal generation."""

from __future__ import annotations

import math
import statistics

from .models import Bar, MarketSnapshot


def build_snapshot(
    symbol: str,
    timeframe: str,
    bars: list[Bar],
    bars_per_year: int | None = None,
) -> MarketSnapshot:
    if len(bars) < 2:
        raise ValueError("at least two bars are required to build a snapshot")
    if not symbol.strip():
        raise ValueError("symbol cannot be empty")
    if not timeframe.strip():
        raise ValueError("timeframe cannot be empty")
    if bars_per_year is not None and bars_per_year <= 0:
        raise ValueError("bars_per_year must be a positive integer")
    closes = [bar.close for bar in bars]
    returns = [current / previous - 1 for previous, current in zip(closes, closes[1:])]
    observed_returns = returns[-20:]
    realised = statistics.stdev(observed_returns) if len(observed_returns) >= 2 else None
    annualised = None
    if realised is not None and bars_per_year is not None:
        annualised = realised * math.sqrt(bars_per_year)
    change = (closes[-1] / closes[max(0, len(closes) - 21)] - 1) * 100
    warnings: list[str] = []
    if bars_per_year is None:
        warnings.append("annualised volatility omitted: supply bars_per_year for this timeframe")
    if len(bars) < 22:
        warnings.append("fewer than 22 bars: 20-period return context is limited")
    return MarketSnapshot(
        symbol=symbol.strip().upper(),
        timeframe=timeframe.strip(),
        bars_count=len(bars),
        latest_timestamp=bars[-1].timestamp.isoformat(),
        latest_close=closes[-1],
        change_pct=change,
        realised_volatility=realised,
        annualised_volatility=annualised,
        bars_per_year=bars_per_year,
        data_warnings=tuple(warnings),
    )
