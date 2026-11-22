import asyncio
import json
from urllib.parse import parse_qs, urlparse

import pytest

from marketcouncil.marketdata import MarketDataError
from marketcouncil.streaming import stream_binance_trades, stream_twelvedata_prices


class FakeSocket:
    def __init__(self, messages):
        self.messages = list(messages)
        self.sent = []

    async def send(self, message):
        self.sent.append(message)

    async def recv(self):
        if not self.messages:
            raise ConnectionError("fake socket exhausted")
        return self.messages.pop(0)

    def __aiter__(self):
        async def iterate():
            for message in self.messages:
                yield message
        return iterate()


class FakeConnection:
    def __init__(self, socket):
        self.socket = socket

    async def __aenter__(self):
        return self.socket

    async def __aexit__(self, *_args):
        return None


class FakeConnectFactory:
    def __init__(self, messages):
        self.socket = FakeSocket(messages)
        self.uri = None
        self.kwargs = None

    def __call__(self, uri, **kwargs):
        self.uri = uri
        self.kwargs = kwargs
        return FakeConnection(self.socket)


def test_twelvedata_stream_normalizes_price_event_and_auth_header():
    messages = [
        json.dumps({"event": "status", "status": "ok"}),
        json.dumps({"event": "price", "symbol": "AAPL", "timestamp": 1700000000, "price": "183.25", "day_volume": "1200"}),
    ]
    factory = FakeConnectFactory(messages)

    async def run():
        result = []
        async for tick in stream_twelvedata_prices(
            ["AAPL"], "equity", api_key="example-key", max_events=1, connect_factory=factory
        ):
            result.append(tick)
        return result

    ticks = asyncio.run(run())
    assert len(ticks) == 1
    assert ticks[0].provider == "twelvedata"
    assert ticks[0].symbol == "AAPL"
    assert ticks[0].price == 183.25
    assert ticks[0].day_volume == 1200
    assert ticks[0].source_timestamp == "2023-11-14T22:13:20+00:00"
    assert factory.uri == "wss://ws.twelvedata.com/v1/quotes/price"
    assert factory.kwargs["additional_headers"]["X-TD-APIKEY"] == "example-key"
    subscribe = json.loads(factory.socket.sent[0])
    assert subscribe == {"action": "subscribe", "params": {"symbols": "AAPL"}}


def test_twelvedata_stream_rejects_unsubscribed_symbol():
    factory = FakeConnectFactory([
        json.dumps({"event": "price", "symbol": "MSFT", "timestamp": 1700000000, "price": "1"})
    ])

    async def run():
        async for _tick in stream_twelvedata_prices(
            ["AAPL"], "equity", api_key="example-key", max_events=1, connect_factory=factory
        ):
            pass

    with pytest.raises(MarketDataError, match="not subscribed"):
        asyncio.run(run())


def test_binance_spot_combined_trade_stream_normalizes_taker_side():
    factory = FakeConnectFactory([
        json.dumps({"stream": "btcusdt@trade", "data": {
            "e": "trade", "E": 1700000000123, "s": "BTCUSDT", "p": "37000.5", "q": "0.01", "T": 1700000000000, "m": True
        }})
    ])

    async def run():
        return [tick async for tick in stream_binance_trades(
            ["BTCUSDT"], market="spot", max_events=1, connect_factory=factory
        )]

    ticks = asyncio.run(run())
    assert len(ticks) == 1
    assert ticks[0].provider == "binance-spot"
    assert ticks[0].asset_class == "crypto"
    assert ticks[0].taker_side == "SELL"
    assert ticks[0].quantity == 0.01
    params = parse_qs(urlparse(factory.uri).query)
    assert params["streams"] == ["btcusdt@trade"]
    assert factory.kwargs["ping_interval"] == 20


def test_binance_usdm_uses_market_stream_and_aggtrade():
    factory = FakeConnectFactory([
        json.dumps({"e": "aggTrade", "E": 1700000000123, "T": 1700000000000, "s": "BTCUSDT", "p": "37000", "q": "0.1", "m": False})
    ])

    async def run():
        return [tick async for tick in stream_binance_trades(
            ["BTCUSDT"], market="usdm", max_events=1, connect_factory=factory
        )]

    ticks = asyncio.run(run())
    assert ticks[0].provider == "binance-usdm"
    assert ticks[0].asset_class == "crypto_futures"
    assert ticks[0].taker_side == "BUY"
    assert factory.uri.startswith("wss://fstream.binance.com/market/stream?")
    assert parse_qs(urlparse(factory.uri).query)["streams"] == ["btcusdt@aggTrade"]


@pytest.mark.parametrize("symbols", [[], ["AAPL;evil"], ["BTCUSDT"] * 51])
def test_streaming_rejects_invalid_symbol_lists(symbols):
    factory = FakeConnectFactory([])

    async def run():
        async for _tick in stream_twelvedata_prices(
            symbols, "equity", api_key="example-key", max_events=1, connect_factory=factory
        ):
            pass

    with pytest.raises(ValueError):
        asyncio.run(run())
    assert factory.uri is None


def test_twelvedata_stream_requires_api_key():
    async def run():
        async for _tick in stream_twelvedata_prices(["AAPL"], "equity", api_key="", connect_factory=lambda *_a, **_k: None):
            pass

    with pytest.raises(ValueError, match="TWELVEDATA_API_KEY"):
        asyncio.run(run())


def test_twelvedata_stream_fails_closed_on_partial_subscription_rejection():
    factory = FakeConnectFactory([
        json.dumps({"event": "subscribe-status", "status": "ok", "success": [{"symbol": "AAPL"}], "fails": [{"symbol": "MSFT", "message": "not entitled"}]})
    ])

    async def run():
        async for _tick in stream_twelvedata_prices(
            ["AAPL", "MSFT"], "equity", api_key="example-key", max_events=1, connect_factory=factory
        ):
            pass

    with pytest.raises(MarketDataError, match="rejected one or more"):
        asyncio.run(run())
