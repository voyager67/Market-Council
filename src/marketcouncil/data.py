"""OHLCV CSV ingestion with strict validation and explicit time handling."""

from __future__ import annotations

import csv
import math
from datetime import UTC, datetime
from pathlib import Path

from .models import Bar

REQUIRED_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume")


class DataValidationError(ValueError):
    """Raised when market data is malformed or ambiguous."""


def _parse_timestamp(value: str, row_number: int) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise DataValidationError(f"row {row_number}: invalid ISO timestamp {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def load_ohlcv_csv(path: str | Path) -> list[Bar]:
    """Load ascending OHLCV rows; naive timestamps are interpreted as UTC."""
    source = Path(path)
    if not source.is_file():
        raise DataValidationError(f"CSV file does not exist: {source}")

    try:
        handle = source.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise DataValidationError(f"cannot read CSV file: {exc}") from exc

    with handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise DataValidationError("CSV is empty or has no header")
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise DataValidationError("duplicate CSV column names are not allowed")
        missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise DataValidationError(f"missing required columns: {', '.join(missing)}")

        bars: list[Bar] = []
        previous: datetime | None = None
        for row_number, row in enumerate(reader, start=2):
            if None in row or any(row.get(column) is None for column in REQUIRED_COLUMNS):
                raise DataValidationError(f"row {row_number}: malformed row width")
            try:
                timestamp = _parse_timestamp(row["timestamp"], row_number)
                values = {
                    name: float(row[name])
                    for name in ("open", "high", "low", "close", "volume")
                }
            except (TypeError, ValueError, KeyError) as exc:
                if isinstance(exc, DataValidationError):
                    raise
                raise DataValidationError(f"row {row_number}: invalid numeric field") from exc

            if not all(math.isfinite(value) for value in values.values()):
                raise DataValidationError(f"row {row_number}: all numeric values must be finite")
            if any(values[name] <= 0 for name in ("open", "high", "low", "close")):
                raise DataValidationError(f"row {row_number}: OHLC prices must be positive")
            if values["volume"] < 0:
                raise DataValidationError(f"row {row_number}: volume cannot be negative")
            if values["high"] < max(values["open"], values["close"], values["low"]):
                raise DataValidationError(f"row {row_number}: high is below another OHLC value")
            if values["low"] > min(values["open"], values["close"], values["high"]):
                raise DataValidationError(f"row {row_number}: low is above another OHLC value")
            if previous is not None and timestamp <= previous:
                relation = "duplicate" if timestamp == previous else "out of order"
                raise DataValidationError(f"row {row_number}: timestamp is {relation}")

            bars.append(Bar(timestamp=timestamp, **values))
            previous = timestamp

    if len(bars) < 2:
        raise DataValidationError("at least two valid OHLCV rows are required")
    return bars
