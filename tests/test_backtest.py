from datetime import UTC, datetime, timedelta

import pytest

from marketcouncil.backtest import BacktestConfig, SmaCrossStrategy, run_backtest
from marketcouncil.models import Bar


def make_bars(closes):
    result = []
    for index, close in enumerate(closes):
        previous = closes[index - 1] if index else close
        result.append(Bar(datetime(2024, 1, 1, tzinfo=UTC) + timedelta(days=index), previous, max(previous, close) + 1, min(previous, close) - 1, close, 1000))
    return result


def test_backtest_signal_executes_on_next_bar_open_and_reports_warning():
    class AlwaysLong:
        name = "always-long"
        def target_exposure(self, history):
            return 1.0

    bars = make_bars([100, 101, 102, 104])
    result = run_backtest(bars, AlwaysLong(), BacktestConfig(initial_equity=1000, commission_bps=0, slippage_bps=0))
    assert result.final_equity > 1000
    assert result.fills[0].timestamp == bars[1].timestamp.isoformat()
    assert result.fills[0].reference_price == bars[1].open
    assert result.fills[-1].side == "SELL"
    assert result.annualised_return_pct is None
    assert any("Annualised" in warning for warning in result.warnings)


def test_backtest_rejects_short_without_explicit_permission():
    class ShortOnly:
        name = "short"
        def target_exposure(self, history):
            return -1.0
    with pytest.raises(ValueError, match="allow_short"):
        run_backtest(make_bars([100, 99, 98]), ShortOnly())


def test_backtest_rejects_lookahead_strategy_exposure_outside_bounds():
    class Bad:
        name = "bad"
        def target_exposure(self, history):
            return 2.0
    with pytest.raises(ValueError, match="between -1 and 1"):
        run_backtest(make_bars([100, 99, 98]), Bad())


def test_sma_strategy_and_config_validation():
    with pytest.raises(ValueError):
        SmaCrossStrategy(10, 5)
    with pytest.raises(ValueError, match="5,000 bps"):
        BacktestConfig(commission_bps=3000, slippage_bps=3000).validate()


def test_backtest_rejects_naive_timestamps_and_malformed_bars():
    naive = Bar(datetime(2024, 1, 1), 100, 101, 99, 100, 100)
    with pytest.raises(ValueError, match="timezone-aware"):
        run_backtest([naive, *make_bars([100, 101, 102])[:2]], SmaCrossStrategy(2, 3))


def test_backtest_stops_when_short_exposure_would_deplete_equity():
    class AlwaysShort:
        name = "always-short"
        def target_exposure(self, history):
            return -1.0

    bars = make_bars([100, 100, 250, 260])
    with pytest.raises(ValueError, match="equity depleted"):
        run_backtest(bars, AlwaysShort(), BacktestConfig(allow_short=True, commission_bps=0, slippage_bps=0))
