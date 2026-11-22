"""Optional, read-only WebSocket market-data streams.

The stream adapters are intentionally small: they normalize provider ticks,
validate payloads, and emit events. They do not maintain books, reconnect,
store ticks, or submit orders. Supervisors should handle reconnect/resubscribe
and persistence according to each venue's sequence and gap-recovery contract.
"""

from __future__ import annotations

import asyncio
import json
import math
import os
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any, AsyncIterator, Callable
from urllib.parse import urlencode

from .marketdata import MarketDataError

MAX_STREAM_SYMBOLS = 50
MAX_STREAM_MESSAGE_BYTES = 1_048_576
DEFAULT_HEARTBEAT_SECONDS = 10.0


@dataclass(frozen=True, slots=True)
class MarketTick:
    provider: str
    symbol: str
    asset_class: str
    event_type: str
    source_timestamp: str | None
    received_at: str
    price: float
    quantity: float | None = None
    day_volume: float | None = None
    taker_side: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_websockets_connect() -> Callable:
    try:
        from websockets.asyncio.client import connect
    except ImportError as exc:
        raise RuntimeError("WebSocket support is optional; install with `pip install -e '.[stream]'`") from exc
    return connect


def _symbols(values: list[str], *, binance: bool = False) -> list[str]:
    if not values or len(values) > MAX_STREAM_SYMBOLS:
        raise ValueError(f"provide between 1 and {MAX_STREAM_SYMBOLS} symbols")
    result: list[str] = []
    for value in values:
        if not isinstance(value, str):
            raise ValueError("symbols must be strings")
        pattern = r"[A-Za-z0-9]{2,30}" if binance else r"[A-Za-z0-9._:/=^!-]{1,50}"
        if not re.fullmatch(pattern, value):
            raise ValueError(f"invalid stream symbol: {value!r}")
        if value.upper() not in {item.upper() for item in result}:
            result.append(value)
    return result


def _source_time(value: Any, *, milliseconds: bool = False) -> str | None:
    if value is None:
        return None
    try:
        timestamp = float(value)
        if not math.isfinite(timestamp):
            return None
        if milliseconds:
            timestamp /= 1000.0
        return datetime.fromtimestamp(timestamp, UTC).isoformat()
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def _finite_positive(value: Any, field: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise MarketDataError(f"stream tick has invalid {field}") from exc
    if not math.isfinite(result) or result <= 0:
        raise MarketDataError(f"stream tick has invalid {field}")
    return result


def _optional_nonnegative(value: Any, field: str) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise MarketDataError(f"stream tick has invalid {field}") from exc
    if not math.isfinite(result) or result < 0:
        raise MarketDataError(f"stream tick has invalid {field}")
    return result


def _decode_message(raw: str | bytes) -> dict[str, Any]:
    if isinstance(raw, bytes):
        if len(raw) > MAX_STREAM_MESSAGE_BYTES:
            raise MarketDataError("WebSocket message exceeded the 1 MiB limit")
        try:
            raw = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise MarketDataError("WebSocket message is not valid UTF-8") from exc
    elif not isinstance(raw, str):
        raise MarketDataError("WebSocket message must be text or UTF-8 bytes")
    if len(raw.encode("utf-8")) > MAX_STREAM_MESSAGE_BYTES:
        raise MarketDataError("WebSocket message exceeded the 1 MiB limit")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise MarketDataError("WebSocket provider returned malformed JSON") from exc
    if not isinstance(payload, dict):
        raise MarketDataError("WebSocket provider returned a non-object event")
    return payload


def _tick_from_twelvedata(payload: dict[str, Any], asset_class: str) -> MarketTick | None:
    event = payload.get("event")
    if event in {"status", "subscribe-status"}:
        if str(payload.get("status", "")).lower() == "error":
            raise MarketDataError(f"Twelve Data stream subscription failed: {str(payload.get('message', 'unknown error'))[:200]}")
        failures = payload.get("fails")
        if isinstance(failures, list) and failures:
            # Do not silently continue with a partially subscribed universe.
            detail = json.dumps(failures, separators=(",", ":"))[:200]
            raise MarketDataError(f"Twelve Data rejected one or more stream symbols: {detail}")
        return None
    if event in {"error", "price-error"} or payload.get("status") == "error":
        raise MarketDataError(f"Twelve Data stream error: {str(payload.get('message', 'unknown error'))[:200]}")
    if event != "price":
        return None
    symbol = payload.get("symbol")
    if not isinstance(symbol, str) or not symbol:
        raise MarketDataError("Twelve Data tick is missing symbol")
    price = _finite_positive(payload.get("price"), "price")
    day_volume = _optional_nonnegative(payload.get("day_volume"), "day_volume")
    return MarketTick(
        provider="twelvedata", symbol=symbol, asset_class=asset_class,
        event_type="price", source_timestamp=_source_time(payload.get("timestamp")),
        received_at=datetime.now(UTC).isoformat(), price=price, day_volume=day_volume,
    )


def _tick_from_binance(payload: dict[str, Any], asset_class: str, provider: str) -> MarketTick | None:
    # Combined streams wrap the actual event in `data`.
    if "data" in payload and isinstance(payload["data"], dict):
        payload = payload["data"]
    event = payload.get("e")
    if event not in {"trade", "aggTrade"}:
        return None
    symbol = payload.get("s")
    if not isinstance(symbol, str) or not re.fullmatch(r"[A-Za-z0-9]{2,30}", symbol):
        raise MarketDataError("Binance tick is missing a valid symbol")
    price = _finite_positive(payload.get("p"), "price")
    quantity = _optional_nonnegative(payload.get("q"), "quantity")
    timestamp = payload.get("T", payload.get("E"))
    buyer_is_maker = payload.get("m")
    taker_side = None
    if isinstance(buyer_is_maker, bool):
        taker_side = "SELL" if buyer_is_maker else "BUY"
    return MarketTick(
        provider=provider, symbol=symbol, asset_class=asset_class,
        event_type=str(event), source_timestamp=_source_time(timestamp, milliseconds=True),
        received_at=datetime.now(UTC).isoformat(), price=price, quantity=quantity,
        taker_side=taker_side,
    )


async def stream_twelvedata_prices(
    symbols: list[str],
    asset_class: str,
    *,
    api_key: str | None = None,
    max_events: int | None = None,
    heartbeat_seconds: float = DEFAULT_HEARTBEAT_SECONDS,
    connect_factory: Callable | None = None,
) -> AsyncIterator[MarketTick]:
    """Yield Twelve Data price events for one asset class.

    Twelve Data accepts mixed-market symbols on one connection, but this
    interface requires one explicit class per invocation to avoid inventing
    classification from provider metadata. API key is passed in an HTTP header
    rather than the URL to avoid leaking it through URL logs.
    """
    if asset_class not in {"equity", "fx", "crypto", "futures"}:
        raise ValueError("Twelve Data supports equity, fx, crypto, or futures asset_class")
    selected = _symbols(symbols)
    if max_events is not None and max_events < 1:
        raise ValueError("max_events must be positive")
    if not math.isfinite(heartbeat_seconds) or not 1 <= heartbeat_seconds <= 60:
        raise ValueError("heartbeat_seconds must be between 1 and 60")
    token = api_key or os.getenv("TWELVEDATA_API_KEY")
    if not token:
        raise ValueError("set TWELVEDATA_API_KEY or pass api_key")
    connect = connect_factory or _load_websockets_connect()
    uri = "wss://ws.twelvedata.com/v1/quotes/price"
    kwargs = {
        "additional_headers": {"X-TD-APIKEY": token},
        "open_timeout": 20,
        "close_timeout": 10,
        "ping_interval": 20,
        "ping_timeout": 20,
        "max_size": MAX_STREAM_MESSAGE_BYTES,
        "compression": None,
    }
    count = 0
    async with connect(uri, **kwargs) as websocket:
        await websocket.send(json.dumps({"action": "subscribe", "params": {"symbols": ",".join(selected)}}))
        loop = asyncio.get_running_loop()
        next_heartbeat = loop.time() + heartbeat_seconds
        while max_events is None or count < max_events:
            wait = max(0.05, next_heartbeat - loop.time())
            try:
                raw = await asyncio.wait_for(websocket.recv(), timeout=wait)
            except asyncio.TimeoutError:
                await websocket.send(json.dumps({"action": "heartbeat"}))
                next_heartbeat = loop.time() + heartbeat_seconds
                continue
            payload = _decode_message(raw)
            tick = _tick_from_twelvedata(payload, asset_class)
            if tick is not None:
                if tick.symbol.upper() not in {item.upper() for item in selected}:
                    raise MarketDataError("Twelve Data emitted a symbol that was not subscribed")
                yield tick
                count += 1


async def stream_binance_trades(
    symbols: list[str],
    *,
    market: str = "spot",
    max_events: int | None = None,
    connect_factory: Callable | None = None,
) -> AsyncIterator[MarketTick]:
    """Yield Binance Spot `trade` or USD-M `aggTrade` events.

    The connection is read-only public market data. A disconnected stream is
    surfaced to the caller; reconnects/resubscriptions require gap-aware logic.
    """
    selected = _symbols(symbols, binance=True)
    if market not in {"spot", "usdm"}:
        raise ValueError("market must be 'spot' or 'usdm'")
    if max_events is not None and max_events < 1:
        raise ValueError("max_events must be positive")
    stream_suffix = "trade" if market == "spot" else "aggTrade"
    streams = [f"{symbol.lower()}@{stream_suffix}" for symbol in selected]
    if market == "spot":
        uri = "wss://stream.binance.com:9443/stream?" + urlencode({"streams": "/".join(streams)})
        asset_class, provider = "crypto", "binance-spot"
    else:
        uri = "wss://fstream.binance.com/market/stream?" + urlencode({"streams": "/".join(streams)})
        asset_class, provider = "crypto_futures", "binance-usdm"
    connect = connect_factory or _load_websockets_connect()
    kwargs = {
        "open_timeout": 20,
        "close_timeout": 10,
        "ping_interval": 20,
        "ping_timeout": 20,
        "max_size": MAX_STREAM_MESSAGE_BYTES,
        "compression": None,
    }
    count = 0
    async with connect(uri, **kwargs) as websocket:
        async for raw in websocket:
            payload = _decode_message(raw)
            tick = _tick_from_binance(payload, asset_class, provider)
            if tick is None:
                continue
            if tick.symbol.upper() not in {item.upper() for item in selected}:
                raise MarketDataError("Binance emitted a symbol that was not subscribed")
            yield tick
            count += 1
            if max_events is not None and count >= max_events:
                return
