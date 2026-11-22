from datetime import UTC, datetime, timedelta

import pytest

from marketcouncil.metrics import build_snapshot
from marketcouncil.models import Bar


def bars(closes):
    result = []
    start = datetime(2026, 1, 1, tzinfo=UTC)
    previous = closes[0]
    for index, close in enumerate(closes):
        result.append(
            Bar(
                timestamp=start + timedelta(days=index),
                open=previous,
                high=max(previous, close) + 1,
                low=min(previous, close) - 1,
                close=close,
                volume=1000,
            )
        )
        previous = close
    return result


def test_snapshot_computes_return_and_volatility():
    result = build_snapshot("abc", "1d", bars([100, 101, 102, 101]), bars_per_year=252)
    assert result.symbol == "ABC"
    assert result.change_pct == pytest.approx(1.0)
    assert result.realised_volatility is not None
    assert result.annualised_volatility is not None


def test_annualisation_is_omitted_without_explicit_factor():
    result = build_snapshot("ABC", "unknown", bars([100, 102, 101]), bars_per_year=None)
    assert result.annualised_volatility is None
    assert any("supply bars_per_year" in item for item in result.data_warnings)


def test_rejects_invalid_bars_per_year():
    with pytest.raises(ValueError):
        build_snapshot("ABC", "1d", bars([100, 101, 102]), bars_per_year=0)


def test_rejects_empty_symbol():
    with pytest.raises(ValueError, match="symbol"):
        build_snapshot(" ", "1d", bars([100, 101, 102]))


def test_rejects_fewer_than_two_bars():
    with pytest.raises(ValueError, match="at least two"):
        build_snapshot("ABC", "1d", bars([100]))
