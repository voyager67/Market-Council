import json
from datetime import UTC, datetime

import pytest

from marketcouncil.marketdata import (
    BinanceKlinesProvider,
    MarketDataError,
    MarketDataRequest,
    TwelveDataProvider,
    write_ohlcv_csv,
)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self, size=-1):
        return self.payload[:size]


def fake_opener(payload, seen=None):
    def opener(request, timeout=20):
        if seen is not None:
            seen.append(request)
        return FakeResponse(payload)
    return opener


def test_binance_public_spot_klines_parse_and_sort():
    rows = [
        [1704067200000, "10", "12", "9", "11", "100", 1704067259999],
        [1704153600000, "11", "13", "10", "12", "120", 1704153659999],
    ]
    seen = []
    provider = BinanceKlinesProvider(opener=fake_opener(json.dumps(rows).encode(), seen))
    bars = provider.fetch_bars(MarketDataRequest("BTCUSDT", "1d", "crypto", limit=2))
    assert [bar.close for bar in bars] == [11, 12]
    assert "api.binance.com" in seen[0].full_url


def test_binance_rejects_asset_class_mismatch():
    provider = BinanceKlinesProvider(opener=fake_opener(b"[]"))
    with pytest.raises(ValueError, match="only supports crypto"):
        provider.fetch_bars(MarketDataRequest("BTCUSDT", "1d", "equity", limit=2))


def test_twelve_data_uses_api_key_header_and_reverses_latest_first_values():
    response = {
        "status": "ok",
        "values": [
            {"datetime": "2024-01-02", "open": "11", "high": "13", "low": "10", "close": "12", "volume": "120"},
            {"datetime": "2024-01-01", "open": "10", "high": "12", "low": "9", "close": "11", "volume": "100"},
        ],
    }
    seen = []
    provider = TwelveDataProvider("secret-test-key", opener=fake_opener(json.dumps(response).encode(), seen))
    bars = provider.fetch_bars(MarketDataRequest("AAPL", "1day", "equity", limit=2))
    assert [bar.close for bar in bars] == [11, 12]
    assert seen[0].get_header("Authorization") == "apikey secret-test-key"


def test_twelve_data_provider_error_is_sanitized():
    provider = TwelveDataProvider("not-a-real-key", opener=fake_opener(b'{"status":"error","message":"bad request"}'))
    with pytest.raises(MarketDataError, match="Twelve Data error"):
        provider.fetch_bars(MarketDataRequest("AAPL", "1day", "equity", limit=2))


def test_fetch_request_requires_aware_time_and_valid_limit():
    request = MarketDataRequest("EUR/USD", "1day", "fx", start=datetime(2024, 1, 1), limit=2)
    with pytest.raises(ValueError, match="timezone-aware"):
        request.validate()


def test_write_ohlcv_csv_roundtrip(tmp_path):
    response = [[1704067200000, "10", "12", "9", "11", "100"], [1704153600000, "11", "13", "10", "12", "120"]]
    bars = BinanceKlinesProvider(opener=fake_opener(json.dumps(response).encode())).fetch_bars(
        MarketDataRequest("BTCUSDT", "1d", "crypto", limit=2)
    )
    path = tmp_path / "out" / "bars.csv"
    write_ohlcv_csv(bars, path)
    assert path.is_file()
    assert path.read_text().splitlines()[0] == "timestamp,open,high,low,close,volume"


def test_twelve_data_omits_outputsize_for_date_bounded_query():
    response = {
        "status": "ok",
        "values": [
            {"datetime": "2024-01-02", "open": "11", "high": "13", "low": "10", "close": "12", "volume": "120"},
            {"datetime": "2024-01-01", "open": "10", "high": "12", "low": "9", "close": "11", "volume": "100"},
        ],
    }
    from datetime import timedelta
    start = datetime(2024, 1, 1, tzinfo=UTC)
    end = start + timedelta(days=2)
    seen = []
    provider = TwelveDataProvider("secret-test-key", opener=fake_opener(json.dumps(response).encode(), seen))
    provider.fetch_bars(MarketDataRequest("AAPL", "1day", "equity", start=start, end=end, limit=2, exchange="NASDAQ"))
    from urllib.parse import parse_qs, urlparse
    params = parse_qs(urlparse(seen[0].full_url).query)
    assert "outputsize" not in params
    assert params["exchange"] == ["NASDAQ"]
    assert "start_date" in params and "end_date" in params


def test_twelve_data_requires_both_date_bounds():
    provider = TwelveDataProvider("secret-test-key", opener=fake_opener(b"{}"))
    with pytest.raises(ValueError, match="both start and end"):
        provider.fetch_bars(MarketDataRequest("AAPL", "1day", "equity", start=datetime(2024, 1, 1, tzinfo=UTC), limit=2))


def test_binance_quote_returns_midpoint_and_book_sizes():
    payload = {"symbol": "BTCUSDT", "bidPrice": "100.0", "bidQty": "1.2", "askPrice": "100.2", "askQty": "2.3"}
    provider = BinanceKlinesProvider(opener=fake_opener(json.dumps(payload).encode()))
    quote = provider.fetch_quote("BTCUSDT", "crypto")
    assert quote.midpoint == pytest.approx(100.1)
    assert quote.last_price is None
    assert quote.source_timestamp is None


def test_twelve_data_quote_reads_source_timestamp():
    payload = {"symbol": "AAPL", "close": "200.5", "timestamp": 1704153600}
    provider = TwelveDataProvider("secret-test-key", opener=fake_opener(json.dumps(payload).encode()))
    quote = provider.fetch_quote("AAPL", "equity", exchange="NASDAQ")
    assert quote.last_price == 200.5
    assert quote.source_timestamp == "2024-01-02T00:00:00+00:00"


def test_market_data_redirect_to_unapproved_host_is_rejected():
    from marketcouncil.marketdata import _http_get

    class RedirectedResponse(FakeResponse):
        def geturl(self):
            return "https://attacker.example/collect"

    def opener(_request, timeout=20):
        return RedirectedResponse(b"should-not-be-read")

    with pytest.raises(MarketDataError, match="redirected outside"):
        _http_get("https://api.binance.com/api/v3/klines", opener=opener)


def test_twelve_data_daily_range_preserves_exchange_local_wall_time():
    from datetime import timedelta, timezone
    from urllib.parse import parse_qs, urlparse

    start = datetime(2024, 1, 1, 9, 30, tzinfo=timezone(timedelta(hours=-5)))
    end = start + timedelta(days=2)
    response = {"status": "ok", "values": [
        {"datetime": "2024-01-02", "open": "11", "high": "13", "low": "10", "close": "12", "volume": "120"},
        {"datetime": "2024-01-01", "open": "10", "high": "12", "low": "9", "close": "11", "volume": "100"},
    ]}
    seen = []
    provider = TwelveDataProvider("secret-test-key", opener=fake_opener(json.dumps(response).encode(), seen))
    provider.fetch_bars(MarketDataRequest("AAPL", "1day", "equity", start=start, end=end, limit=2))
    params = parse_qs(urlparse(seen[0].full_url).query)
    assert params["start_date"] == ["2024-01-01 09:30:00"]
    assert params["end_date"] == ["2024-01-03 09:30:00"]


def test_twelve_data_quote_does_not_assume_naive_datetime_is_utc():
    payload = {"symbol": "AAPL", "close": "200.5", "datetime": "2024-01-02 09:30:00"}
    provider = TwelveDataProvider("secret-test-key", opener=fake_opener(json.dumps(payload).encode()))
    quote = provider.fetch_quote("AAPL", "equity", exchange="NASDAQ")
    assert quote.source_timestamp is None
