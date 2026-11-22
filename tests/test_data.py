from pathlib import Path

import pytest

from marketcouncil.data import DataValidationError, load_ohlcv_csv


def write_csv(tmp_path: Path, rows: str) -> Path:
    path = tmp_path / "bars.csv"
    path.write_text(
        "timestamp,open,high,low,close,volume\n" + rows,
        encoding="utf-8",
    )
    return path


def test_loads_valid_rows_and_normalizes_timezone(tmp_path):
    path = write_csv(
        tmp_path,
        "2026-01-01T09:00:00+05:30,100,102,99,101,1000\n"
        "2026-01-02T09:00:00+05:30,101,103,100,102,1200\n",
    )
    bars = load_ohlcv_csv(path)
    assert len(bars) == 2
    assert bars[0].timestamp.isoformat() == "2026-01-01T03:30:00+00:00"


def test_naive_timestamps_are_utc(tmp_path):
    path = write_csv(
        tmp_path,
        "2026-01-01T09:00:00,100,102,99,101,1000\n"
        "2026-01-02T09:00:00,101,103,100,102,1200\n",
    )
    assert load_ohlcv_csv(path)[0].timestamp.utcoffset().total_seconds() == 0


def test_rejects_missing_columns(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("timestamp,open,close\n2026-01-01,1,1\n", encoding="utf-8")
    with pytest.raises(DataValidationError, match="missing required columns"):
        load_ohlcv_csv(path)


def test_rejects_duplicate_timestamp(tmp_path):
    path = write_csv(
        tmp_path,
        "2026-01-01T00:00:00Z,100,102,99,101,1000\n"
        "2026-01-01T00:00:00+00:00,101,103,100,102,1200\n",
    )
    with pytest.raises(DataValidationError, match="duplicate"):
        load_ohlcv_csv(path)


def test_rejects_out_of_order_timestamp(tmp_path):
    path = write_csv(
        tmp_path,
        "2026-01-02T00:00:00Z,100,102,99,101,1000\n"
        "2026-01-01T00:00:00Z,101,103,100,102,1200\n",
    )
    with pytest.raises(DataValidationError, match="out of order"):
        load_ohlcv_csv(path)


def test_rejects_invalid_high_low_range(tmp_path):
    path = write_csv(
        tmp_path,
        "2026-01-01T00:00:00Z,100,99,98,101,1000\n"
        "2026-01-02T00:00:00Z,101,103,100,102,1200\n",
    )
    with pytest.raises(DataValidationError, match="high"):
        load_ohlcv_csv(path)


def test_rejects_negative_volume(tmp_path):
    path = write_csv(
        tmp_path,
        "2026-01-01T00:00:00Z,100,102,99,101,-1\n"
        "2026-01-02T00:00:00Z,101,103,100,102,1200\n",
    )
    with pytest.raises(DataValidationError, match="volume"):
        load_ohlcv_csv(path)


def test_rejects_non_finite_prices(tmp_path):
    path = write_csv(
        tmp_path,
        "2026-01-01T00:00:00Z,100,102,99,nan,1000\n"
        "2026-01-02T00:00:00Z,101,103,100,102,1200\n",
    )
    with pytest.raises(DataValidationError, match="finite"):
        load_ohlcv_csv(path)


def test_rejects_one_bar(tmp_path):
    path = write_csv(tmp_path, "2026-01-01T00:00:00Z,100,102,99,101,1000\n")
    with pytest.raises(DataValidationError, match="at least two"):
        load_ohlcv_csv(path)


def test_rejects_missing_file(tmp_path):
    with pytest.raises(DataValidationError, match="does not exist"):
        load_ohlcv_csv(tmp_path / "missing.csv")


def test_rejects_duplicate_column_names(tmp_path):
    path = tmp_path / "duplicate.csv"
    path.write_text(
        "timestamp,open,high,low,close,volume,close\n"
        "2026-01-01,100,102,99,101,1000,101\n"
        "2026-01-02,101,103,100,102,1200,102\n",
        encoding="utf-8",
    )
    with pytest.raises(DataValidationError, match="duplicate CSV column"):
        load_ohlcv_csv(path)


def test_rejects_malformed_row_width(tmp_path):
    path = write_csv(
        tmp_path,
        "2026-01-01T00:00:00Z,100,102,99,101,1000,unexpected\n"
        "2026-01-02T00:00:00Z,101,103,100,102,1200\n",
    )
    with pytest.raises(DataValidationError, match="malformed row width"):
        load_ohlcv_csv(path)
