import math

import pytest

from marketcouncil.risk import calculate_position_size


def test_long_position_respects_risk_budget():
    result = calculate_position_size(
        equity=100_000, risk_pct=0.5, entry=100, stop=95, side="long"
    )
    assert result.units == 100
    assert result.estimated_stop_loss <= result.risk_budget


def test_short_position_respects_risk_budget():
    result = calculate_position_size(
        equity=100_000, risk_pct=1, entry=100, stop=105, side="short"
    )
    assert result.units == 200


def test_position_cap_can_bind_before_risk_budget():
    result = calculate_position_size(
        equity=100_000,
        risk_pct=5,
        entry=100,
        stop=99,
        side="long",
        max_position_pct=10,
    )
    assert result.units == 100
    assert result.cap_was_binding is True


def test_fee_and_slippage_increase_risk_per_unit():
    plain = calculate_position_size(equity=10_000, risk_pct=1, entry=50, stop=49, side="long")
    friction = calculate_position_size(
        equity=10_000,
        risk_pct=1,
        entry=50,
        stop=49,
        side="long",
        fee_pct=0.1,
        slippage_pct=0.2,
    )
    assert friction.risk_per_unit > plain.risk_per_unit
    assert friction.units < plain.units


@pytest.mark.parametrize(
    "kwargs",
    [
        {"equity": 0, "risk_pct": 1, "entry": 10, "stop": 9, "side": "long"},
        {"equity": 10_000, "risk_pct": 0, "entry": 10, "stop": 9, "side": "long"},
        {"equity": 10_000, "risk_pct": 1, "entry": 10, "stop": 11, "side": "long"},
        {"equity": 10_000, "risk_pct": 1, "entry": 10, "stop": 9, "side": "short"},
        {"equity": 10_000, "risk_pct": 1, "entry": 10, "stop": 9, "side": "buy"},
    ],
)
def test_rejects_invalid_inputs(kwargs):
    with pytest.raises(ValueError):
        calculate_position_size(**kwargs)


def test_rejects_nan_and_infinity():
    for value in (math.nan, math.inf):
        with pytest.raises(ValueError, match="finite"):
            calculate_position_size(
                equity=10_000, risk_pct=1, entry=value, stop=9, side="long"
            )


def test_units_never_exceed_fractional_risk_budget_due_to_rounding():
    result = calculate_position_size(
        equity=100_000, risk_pct=0.25, entry=103.7, stop=101.9,
        side="long", fee_pct=0.035, slippage_pct=0.04,
    )
    assert result.estimated_stop_loss <= result.risk_budget
