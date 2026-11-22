"""Deterministic position-sizing arithmetic with explicit assumptions."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from decimal import Decimal, ROUND_FLOOR, localcontext


@dataclass(frozen=True, slots=True)
class SizingResult:
    side: str
    risk_budget: float
    risk_per_unit: float
    units: int
    notional: float
    estimated_stop_loss: float
    position_cap_notional: float
    cap_was_binding: bool

    def to_dict(self) -> dict[str, float | int | str | bool]:
        return asdict(self)


def calculate_position_size(
    *,
    equity: float,
    risk_pct: float,
    entry: float,
    stop: float,
    side: str,
    fee_pct: float = 0.0,
    slippage_pct: float = 0.0,
    max_position_pct: float = 100.0,
) -> SizingResult:
    """Calculate units under risk and notional caps; percentages use 0–100 units."""
    numeric = {
        "equity": equity,
        "risk_pct": risk_pct,
        "entry": entry,
        "stop": stop,
        "fee_pct": fee_pct,
        "slippage_pct": slippage_pct,
        "max_position_pct": max_position_pct,
    }
    if not all(math.isfinite(value) for value in numeric.values()):
        raise ValueError("all numeric inputs must be finite")
    if equity <= 0 or entry <= 0 or stop <= 0:
        raise ValueError("equity, entry, and stop must be positive")
    if not 0 < risk_pct <= 100:
        raise ValueError("risk_pct must be greater than 0 and at most 100")
    if not 0 < max_position_pct <= 100:
        raise ValueError("max_position_pct must be greater than 0 and at most 100")
    if fee_pct < 0 or slippage_pct < 0:
        raise ValueError("fee and slippage percentages cannot be negative")
    side = side.lower()
    if side not in {"long", "short"}:
        raise ValueError("side must be 'long' or 'short'")
    if side == "long" and stop >= entry:
        raise ValueError("a long position requires stop < entry")
    if side == "short" and stop <= entry:
        raise ValueError("a short position requires stop > entry")

    # Decimal(str(...)) avoids binary-float drift at exact unit boundaries.
    with localcontext() as context:
        context.prec = 28
        dec_equity = Decimal(str(equity))
        dec_risk_pct = Decimal(str(risk_pct))
        dec_entry = Decimal(str(entry))
        dec_stop = Decimal(str(stop))
        dec_fee = Decimal(str(fee_pct))
        dec_slippage = Decimal(str(slippage_pct))
        dec_cap_pct = Decimal(str(max_position_pct))
        risk_budget = dec_equity * dec_risk_pct / Decimal("100")
        friction_per_unit = dec_entry * (dec_fee + dec_slippage) / Decimal("100")
        risk_per_unit = abs(dec_entry - dec_stop) + friction_per_unit
        risk_units = int((risk_budget / risk_per_unit).to_integral_value(rounding=ROUND_FLOOR))
        position_cap = dec_equity * dec_cap_pct / Decimal("100")
        cap_units = int((position_cap / dec_entry).to_integral_value(rounding=ROUND_FLOOR))
        units = max(0, min(risk_units, cap_units))
        estimated_loss = Decimal(units) * risk_per_unit
        notional = Decimal(units) * dec_entry
    return SizingResult(
        side=side,
        risk_budget=float(risk_budget),
        risk_per_unit=float(risk_per_unit),
        units=units,
        notional=float(notional),
        estimated_stop_loss=float(estimated_loss),
        position_cap_notional=float(position_cap),
        cap_was_binding=cap_units < risk_units,
    )
