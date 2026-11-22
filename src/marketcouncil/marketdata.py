"""Optional market-data connectors for equities, FX, crypto, and futures.

All HTTP access is HTTPS-only, host-allowlisted, bounded, and injectable for tests.
No provider is silently selected: callers choose a source and own its terms/limits.
"""

from __future__ import annotations

import csv
import json
import math
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from collections.abc import Callable
from typing import Protocol

from .models import Bar

MAX_RESPONSE_BYTES = 10 * 1024 * 1024
DEFAULT_TIMEOUT = 20.0


class MarketDataError(RuntimeError):
    """Provider, transport, or response-validation error."""


@dataclass(frozen=True, slots=True)
class MarketDataRequest:
    symbol: str
    interval: str
    asset_class: str
    start: datetime | None = None
    end: datetime | None = None
    limit: int = 1000
    exchange: str | None = None
    mic_code: str | None = None

    def validate(self) -> None:
        if not re.fullmatch(r"[A-Za-z0-9._:/=^!-]{1,50}", self.symbol):
            raise ValueError("symbol contains unsupported characters")
        if self.asset_class not in {"equity", "fx", "crypto", "futures", "crypto_futures"}:
            raise ValueError("asset_class must be equity, fx, crypto, futures, or crypto_futures")
        if not re.fullmatch(r"[1-9][0-9]*(?:min|h|day|week|month)", self.interval) and self.interval not in {
            "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"
        }:
            raise ValueError("unsupported interval syntax")
        if not 2 <= self.limit <= 5000:
            raise ValueError("limit must be between 2 and 5000")
        for label, value in (("start", self.start), ("end", self.end)):
            if value is not None and (value.tzinfo is None or value.utcoffset() is None):
                raise ValueError(f"{label} must be timezone-aware")
        if self.start and self.end and self.start >= self.end:
            raise ValueError("start must be earlier than end")
        for label, value in (("exchange", self.exchange), ("mic_code", self.mic_code)):
            if value is not None and not re.fullmatch(r"[A-Za-z0-9._-]{1,20}", value):
                raise ValueError(f"{label} contains unsupported characters")


@dataclass(frozen=True, slots=True)
class QuoteSnapshot:
    symbol: str
    asset_class: str
    provider: str
    observed_at: str
    source_timestamp: str | None
    last_price: float | None
    bid: float | None = None
    ask: float | None = None
    bid_size: float | None = None
    ask_size: float | None = None

    @property
    def midpoint(self) -> float | None:
        if self.bid is not None and self.ask is not None:
            return (self.bid + self.ask) / 2
        return self.last_price

    def to_dict(self) -> dict:
        result = asdict(self)
        result["midpoint"] = self.midpoint
        return result


class MarketDataProvider(Protocol):
    name: str

    def fetch_bars(self, request: MarketDataRequest) -> list[Bar]: ...


def _http_get(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    opener: Callable = urllib.request.urlopen,
) -> bytes:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in {"api.binance.com", "fapi.binance.com", "api.twelvedata.com"}:
        raise MarketDataError("provider endpoint is not on the HTTPS allowlist")
    if not 1 <= timeout <= 120:
        raise ValueError("timeout must be between 1 and 120 seconds")
    request = urllib.request.Request(url, headers=headers or {}, method="GET")
    try:
        with opener(request, timeout=timeout) as response:
            # urllib follows redirects by default. Validate the final URL too so
            # an allowlisted provider cannot redirect a credential-bearing call
            # to an unrelated host.
            final_url = response.geturl() if hasattr(response, "geturl") else url
            final = urllib.parse.urlparse(final_url)
            if final.scheme != "https" or final.hostname != parsed.hostname:
                raise MarketDataError("market-data provider redirected outside its HTTPS host")
            payload = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise MarketDataError(f"market-data provider returned HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise MarketDataError(f"market-data request failed: {type(exc).__name__}") from exc
    if len(payload) > MAX_RESPONSE_BYTES:
        raise MarketDataError("market-data response exceeded the 10 MiB limit")
    return payload


def _parse_datetime(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise MarketDataError(f"provider returned invalid timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _validate_bars(bars: list[Bar], *, limit: int) -> list[Bar]:
    if len(bars) < 2:
        raise MarketDataError("provider returned fewer than two bars")
    if len(bars) > limit:
        raise MarketDataError(f"provider returned {len(bars)} bars, above the requested limit {limit}; narrow the date range")
    previous: datetime | None = None
    for bar in bars:
        values = (bar.open, bar.high, bar.low, bar.close, bar.volume)
        if not all(math.isfinite(v) for v in values):
            raise MarketDataError("provider returned non-finite OHLCV values")
        if min(bar.open, bar.high, bar.low, bar.close) <= 0 or bar.volume < 0:
            raise MarketDataError("provider returned non-positive prices or negative volume")
        if bar.high < max(bar.open, bar.close, bar.low) or bar.low > min(bar.open, bar.close, bar.high):
            raise MarketDataError("provider returned inconsistent OHLC bounds")
        if previous is not None and bar.timestamp <= previous:
            raise MarketDataError("provider bars are duplicate or not strictly ascending")
        previous = bar.timestamp
    return bars


class CSVMarketDataProvider:
    name = "csv"

    def fetch_bars(self, request: MarketDataRequest, path: str | Path) -> list[Bar]:
        from .data import load_ohlcv_csv

        request.validate()
        bars = load_ohlcv_csv(path)
        if request.start:
            bars = [item for item in bars if item.timestamp >= request.start.astimezone(UTC)]
        if request.end:
            bars = [item for item in bars if item.timestamp <= request.end.astimezone(UTC)]
        return _validate_bars(bars, limit=request.limit)


class BinanceKlinesProvider:
    """Public Binance spot or USD-M perpetual/futures klines (no trading endpoints)."""

    name = "binance"
    INTERVALS = {"1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"}

    def __init__(
        self,
        *,
        market: str = "spot",
        timeout: float = DEFAULT_TIMEOUT,
        opener: Callable = urllib.request.urlopen,
    ) -> None:
        if market not in {"spot", "usdm"}:
            raise ValueError("market must be 'spot' or 'usdm'")
        self.market = market
        self.timeout = timeout
        self.opener = opener

    def fetch_bars(self, request: MarketDataRequest) -> list[Bar]:
        request.validate()
        if request.interval not in self.INTERVALS:
            raise ValueError("Binance interval is unsupported")
        if self.market == "spot" and request.asset_class != "crypto":
            raise ValueError("Binance spot adapter only supports crypto asset_class")
        if self.market == "usdm" and request.asset_class != "crypto_futures":
            raise ValueError("Binance USD-M adapter only supports crypto_futures asset_class")
        host = "https://api.binance.com" if self.market == "spot" else "https://fapi.binance.com"
        endpoint = "/api/v3/klines" if self.market == "spot" else "/fapi/v1/klines"
        cursor = int(request.start.timestamp() * 1000) if request.start else None
        end_ms = int(request.end.timestamp() * 1000) if request.end else None
        bars: list[Bar] = []
        while len(bars) < request.limit:
            params: dict[str, str | int] = {"symbol": request.symbol.upper(), "interval": request.interval, "limit": min(1000, request.limit - len(bars))}
            if cursor is not None:
                params["startTime"] = cursor
            if end_ms is not None:
                params["endTime"] = end_ms
            url = f"{host}{endpoint}?{urllib.parse.urlencode(params)}"
            raw = _http_get(url, timeout=self.timeout, opener=self.opener)
            try:
                rows = json.loads(raw)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise MarketDataError("Binance returned malformed JSON") from exc
            if not isinstance(rows, list):
                message = rows.get("msg", "unexpected provider response") if isinstance(rows, dict) else "unexpected provider response"
                raise MarketDataError(f"Binance error: {str(message)[:240]}")
            if not rows:
                break
            for row in rows:
                if not isinstance(row, list) or len(row) < 6:
                    raise MarketDataError("Binance returned malformed kline row")
                try:
                    bars.append(Bar(
                        timestamp=datetime.fromtimestamp(int(row[0]) / 1000, UTC),
                        open=float(row[1]), high=float(row[2]), low=float(row[3]),
                        close=float(row[4]), volume=float(row[5]),
                    ))
                except (TypeError, ValueError, OverflowError) as exc:
                    raise MarketDataError("Binance returned invalid kline values") from exc
            last_open_ms = int(rows[-1][0])
            next_cursor = last_open_ms + 1
            if cursor is not None and next_cursor <= cursor:
                raise MarketDataError("Binance pagination did not advance")
            cursor = next_cursor
            if len(rows) < min(1000, request.limit - (len(bars) - len(rows))):
                break
        bars = [bar for bar in bars if (request.start is None or bar.timestamp >= request.start.astimezone(UTC)) and (request.end is None or bar.timestamp <= request.end.astimezone(UTC))]
        return _validate_bars(bars, limit=request.limit)

    def fetch_quote(self, symbol: str, asset_class: str) -> QuoteSnapshot:
        if not re.fullmatch(r"[A-Za-z0-9]{2,30}", symbol):
            raise ValueError("Binance symbol must contain 2-30 letters or digits")
        if self.market == "spot" and asset_class != "crypto":
            raise ValueError("Binance spot quote adapter only supports crypto")
        if self.market == "usdm" and asset_class != "crypto_futures":
            raise ValueError("Binance USD-M quote adapter only supports crypto_futures")
        host = "https://api.binance.com" if self.market == "spot" else "https://fapi.binance.com"
        endpoint = "/api/v3/ticker/bookTicker" if self.market == "spot" else "/fapi/v1/ticker/bookTicker"
        url = f"{host}{endpoint}?{urllib.parse.urlencode({'symbol': symbol.upper()})}"
        try:
            payload = json.loads(_http_get(url, timeout=self.timeout, opener=self.opener))
            bid = float(payload["bidPrice"])
            ask = float(payload["askPrice"])
            bid_size = float(payload["bidQty"])
            ask_size = float(payload["askQty"])
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise MarketDataError("Binance returned an invalid order-book quote") from exc
        if not all(math.isfinite(v) for v in (bid, ask, bid_size, ask_size)) or bid <= 0 or ask < bid or bid_size < 0 or ask_size < 0:
            raise MarketDataError("Binance returned an invalid or crossed best bid/ask")
        source_timestamp = None
        if isinstance(payload, dict) and payload.get("time") is not None:
            source_timestamp = datetime.fromtimestamp(int(payload["time"]) / 1000, UTC).isoformat()
        return QuoteSnapshot(
            symbol=symbol.upper(), asset_class=asset_class, provider=f"binance-{self.market}",
            observed_at=datetime.now(UTC).isoformat(), source_timestamp=source_timestamp,
            last_price=None, bid=bid, ask=ask, bid_size=bid_size, ask_size=ask_size,
        )


class TwelveDataProvider:
    """Twelve Data time-series adapter; plan coverage depends on the account."""

    name = "twelvedata"

    def __init__(
        self,
        api_key: str | None = None,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        opener: Callable = urllib.request.urlopen,
    ) -> None:
        self.api_key = api_key or os.getenv("TWELVEDATA_API_KEY")
        if not self.api_key:
            raise ValueError("set TWELVEDATA_API_KEY or pass api_key")
        self.timeout = timeout
        self.opener = opener

    def fetch_bars(self, request: MarketDataRequest) -> list[Bar]:
        request.validate()
        if bool(request.start) != bool(request.end):
            raise ValueError("Twelve Data date filtering requires both start and end")
        params = {
            "symbol": request.symbol,
            "interval": request.interval,
            "timezone": "UTC",
            "format": "JSON",
        }
        if request.exchange:
            params["exchange"] = request.exchange
        if request.mic_code:
            params["mic_code"] = request.mic_code
        # Twelve Data interprets daily/weekly/monthly range boundaries in the
        # instrument's exchange-local timezone and ignores the `timezone`
        # parameter for those intervals. Preserve the supplied wall-clock
        # boundary for those bars; intraday is explicitly requested in UTC.
        session_interval = request.interval in {"1day", "1week", "1month"}

        def format_bound(value: datetime) -> str:
            if session_interval:
                return value.strftime("%Y-%m-%d %H:%M:%S")
            return value.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S")

        if request.start:
            params["start_date"] = format_bound(request.start)
        if request.end:
            params["end_date"] = format_bound(request.end)
        # Twelve Data documents that outputsize truncates a date-bounded query;
        # omit it whenever an explicit date range is supplied.
        if not (request.start and request.end):
            params["outputsize"] = str(min(request.limit, 5000))
        url = "https://api.twelvedata.com/time_series?" + urllib.parse.urlencode(params)
        raw = _http_get(url, headers={"Authorization": f"apikey {self.api_key}"}, timeout=self.timeout, opener=self.opener)
        try:
            payload = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise MarketDataError("Twelve Data returned malformed JSON") from exc
        if not isinstance(payload, dict) or payload.get("status") == "error" or not isinstance(payload.get("values"), list):
            message = payload.get("message", "unexpected provider response") if isinstance(payload, dict) else "unexpected provider response"
            raise MarketDataError(f"Twelve Data error: {str(message)[:240]}")
        bars: list[Bar] = []
        for row in reversed(payload["values"]):
            try:
                bars.append(Bar(
                    timestamp=_parse_datetime(str(row["datetime"])),
                    open=float(row["open"]), high=float(row["high"]),
                    low=float(row["low"]), close=float(row["close"]),
                    volume=float(row.get("volume") or 0),
                ))
            except (KeyError, TypeError, ValueError) as exc:
                raise MarketDataError("Twelve Data returned an invalid OHLCV row") from exc
        return _validate_bars(bars, limit=request.limit)

    def fetch_quote(self, symbol: str, asset_class: str, exchange: str | None = None, mic_code: str | None = None) -> QuoteSnapshot:
        if asset_class not in {"equity", "fx", "crypto", "futures"}:
            raise ValueError("Twelve Data quote adapter supports equity, fx, crypto, and futures classifications")
        if not re.fullmatch(r"[A-Za-z0-9._:/=^!-]{1,50}", symbol):
            raise ValueError("symbol contains unsupported characters")
        params = {"symbol": symbol, "format": "JSON"}
        if exchange:
            if not re.fullmatch(r"[A-Za-z0-9._-]{1,20}", exchange):
                raise ValueError("exchange contains unsupported characters")
            params["exchange"] = exchange
        if mic_code:
            if not re.fullmatch(r"[A-Za-z0-9._-]{1,20}", mic_code):
                raise ValueError("mic_code contains unsupported characters")
            params["mic_code"] = mic_code
        url = "https://api.twelvedata.com/quote?" + urllib.parse.urlencode(params)
        try:
            payload = json.loads(_http_get(url, headers={"Authorization": f"apikey {self.api_key}"}, timeout=self.timeout, opener=self.opener))
            last = float(payload["close"])
            timestamp = payload.get("timestamp")
            if timestamp is not None:
                source_timestamp = datetime.fromtimestamp(int(timestamp), UTC).isoformat()
            else:
                # A naive quote datetime is normally exchange-local. Do not
                # invent UTC semantics when the provider omits its epoch time.
                raw_datetime = payload.get("datetime")
                parsed_datetime = (
                    datetime.fromisoformat(str(raw_datetime).replace("Z", "+00:00"))
                    if raw_datetime is not None else None
                )
                source_timestamp = (
                    parsed_datetime.astimezone(UTC).isoformat()
                    if parsed_datetime is not None and parsed_datetime.tzinfo is not None
                    else None
                )
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError, OverflowError) as exc:
            raise MarketDataError("Twelve Data returned an invalid quote response") from exc
        if not math.isfinite(last) or last <= 0:
            raise MarketDataError("Twelve Data quote price must be finite and positive")
        return QuoteSnapshot(
            symbol=symbol.upper(), asset_class=asset_class, provider="twelvedata",
            observed_at=datetime.now(UTC).isoformat(), source_timestamp=source_timestamp,
            last_price=last,
        )


def write_ohlcv_csv(bars: list[Bar], path: str | Path) -> None:
    """Write validated bars in the canonical MarketCouncil CSV format."""
    validated = _validate_bars(bars, limit=max(2, len(bars)))
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("timestamp", "open", "high", "low", "close", "volume"))
        for bar in validated:
            writer.writerow((bar.timestamp.isoformat(), bar.open, bar.high, bar.low, bar.close, bar.volume))
