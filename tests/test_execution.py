import hashlib
import hmac
import json
from urllib.parse import parse_qs, urlparse

import pytest

from marketcouncil.execution import BinanceSpotTestnetAdapter


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return None
    def read(self, size=-1):
        return self.payload[:size]


def test_binance_adapter_signs_only_spot_testnet_limit_order():
    payload = {"symbol":"BTCUSDT","orderId":123,"clientOrderId":"mc-1","status":"NEW","side":"BUY","type":"LIMIT","origQty":"0.01","price":"50000"}
    seen = []
    def opener(request, timeout=10):
        seen.append(request)
        return FakeResponse(json.dumps(payload).encode())
    adapter = BinanceSpotTestnetAdapter("test-key", "test-secret", opener=opener)
    result = adapter.place_limit_order(symbol="BTCUSDT", side="BUY", quantity=0.01, price=50000, client_order_id="mc-1")
    request = seen[0]
    assert urlparse(request.full_url).hostname == "testnet.binance.vision"
    assert request.get_method() == "POST"
    assert request.get_header("X-mbx-apikey") == "test-key"
    query = urlparse(request.full_url).query
    params = parse_qs(query)
    supplied = params.pop("signature")[0]
    canonical = "&".join(f"{key}={values[0]}" for key, values in params.items())
    expected = hmac.new(b"test-secret", canonical.encode(), hashlib.sha256).hexdigest()
    assert supplied == expected
    assert result.order_id == 123
    assert result.to_dict()["real_money"] is False
    assert "raw_response" not in result.to_dict()


def test_testnet_adapter_requires_sandbox_credentials():
    with pytest.raises(ValueError, match="BINANCE_TESTNET"):
        BinanceSpotTestnetAdapter("", "")


def test_testnet_adapter_rejects_bad_order_inputs_before_network():
    adapter = BinanceSpotTestnetAdapter("key", "secret", opener=lambda *args, **kwargs: pytest.fail("network must not be called"))
    with pytest.raises(ValueError, match="side"):
        adapter.place_limit_order(symbol="BTCUSDT", side="BUYSELL", quantity=1, price=10)
    with pytest.raises(ValueError, match="positive"):
        adapter.place_limit_order(symbol="BTCUSDT", side="BUY", quantity=1, price=float("nan"))


def test_alpaca_adapter_is_paper_endpoint_only_and_sanitizes_result():
    from marketcouncil.execution import AlpacaPaperAdapter
    payload = {"id":"paper-order-1","client_order_id":"mc-paper-1","status":"accepted","qty":"2","limit_price":"190.25"}
    seen = []
    def opener(request, timeout=10):
        seen.append(request)
        return FakeResponse(json.dumps(payload).encode())
    adapter = AlpacaPaperAdapter("paper-key", "paper-secret", opener=opener)
    result = adapter.place_limit_order(symbol="AAPL", side="buy", quantity=2, limit_price=190.25, client_order_id="mc-paper-1")
    request = seen[0]
    assert urlparse(request.full_url).hostname == "paper-api.alpaca.markets"
    assert request.get_method() == "POST"
    assert request.get_header("Apca-api-key-id") == "paper-key"
    assert result.order_id == "paper-order-1"
    assert result.to_dict()["environment"] == "ALPACA_PAPER"
    assert result.to_dict()["real_money"] is False


def test_alpaca_adapter_requires_paper_credentials_and_limit_price():
    from marketcouncil.execution import AlpacaPaperAdapter
    with pytest.raises(ValueError, match="ALPACA_PAPER"):
        AlpacaPaperAdapter("", "")
    adapter = AlpacaPaperAdapter("key", "secret", opener=lambda *args, **kwargs: pytest.fail("network must not be called"))
    with pytest.raises(ValueError, match="positive"):
        adapter.place_limit_order(symbol="AAPL", side="buy", quantity=1, limit_price=0)
