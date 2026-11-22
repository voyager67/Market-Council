"""Explicit sandbox execution adapters. No mainnet/live-money adapter is provided."""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Callable


class ExecutionError(RuntimeError):
    """Sandbox order submission error; status may be unknown after transport failure."""


@dataclass(frozen=True, slots=True)
class TestnetOrderResult:
    environment: str
    symbol: str
    order_id: int | None
    client_order_id: str | None
    status: str
    side: str
    order_type: str
    original_quantity: str | None
    price: str | None
    raw_response: dict

    def to_dict(self) -> dict:
        return {
            "environment": self.environment, "symbol": self.symbol,
            "order_id": self.order_id, "client_order_id": self.client_order_id,
            "status": self.status, "side": self.side, "order_type": self.order_type,
            "original_quantity": self.original_quantity, "price": self.price,
            "real_money": False,
        }


class BinanceSpotTestnetAdapter:
    """Place LIMIT orders only on Binance Spot testnet (testnet.binance.vision)."""

    BASE_URL = "https://testnet.binance.vision"

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        *,
        timeout: float = 10.0,
        opener: Callable = urllib.request.urlopen,
    ) -> None:
        self.api_key = api_key or os.getenv("BINANCE_TESTNET_API_KEY")
        self.api_secret = api_secret or os.getenv("BINANCE_TESTNET_SECRET")
        if not self.api_key or not self.api_secret:
            raise ValueError("set BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_SECRET for sandbox credentials")
        if not 1 <= timeout <= 30:
            raise ValueError("timeout must be between 1 and 30 seconds")
        self.timeout = timeout
        self.opener = opener

    def place_limit_order(
        self, *, symbol: str, side: str, quantity: float, price: float,
        time_in_force: str = "GTC", client_order_id: str | None = None,
    ) -> TestnetOrderResult:
        symbol = symbol.upper()
        side = side.upper()
        if not re.fullmatch(r"[A-Z0-9]{2,30}", symbol):
            raise ValueError("invalid testnet symbol")
        if side not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")
        if not math.isfinite(quantity) or not math.isfinite(price) or quantity <= 0 or price <= 0:
            raise ValueError("quantity and price must be finite and positive")
        if time_in_force not in {"GTC", "IOC", "FOK"}:
            raise ValueError("time_in_force must be GTC, IOC, or FOK")
        if client_order_id is not None and not re.fullmatch(r"[A-Za-z0-9_-]{1,36}", client_order_id):
            raise ValueError("client_order_id must be 1-36 alphanumeric, underscore, or dash characters")

        params = {
            "symbol": symbol, "side": side, "type": "LIMIT",
            "timeInForce": time_in_force, "quantity": format(quantity, ".12g"),
            "price": format(price, ".12g"), "recvWindow": 5000,
            "timestamp": int(time.time() * 1000),
        }
        if client_order_id:
            params["newClientOrderId"] = client_order_id
        query = urllib.parse.urlencode(params)
        signature = hmac.new(self.api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
        url = f"{self.BASE_URL}/api/v3/order?{query}&signature={signature}"
        request = urllib.request.Request(url, headers={"X-MBX-APIKEY": self.api_key}, method="POST")
        try:
            with self.opener(request, timeout=self.timeout) as response:
                raw = response.read(1_000_001)
        except urllib.error.HTTPError as exc:
            try:
                body = exc.read(4096).decode("utf-8", errors="replace")
            except OSError:
                body = ""
            raise ExecutionError(f"Binance testnet rejected the order (HTTP {exc.code}): {body[:300]}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ExecutionError("Binance testnet transport failed; order status may be unknown, reconcile by client_order_id before retrying") from exc
        if len(raw) > 1_000_000:
            raise ExecutionError("Binance testnet response exceeded 1 MB")
        try:
            payload = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ExecutionError("Binance testnet returned malformed JSON; order status may be unknown") from exc
        if not isinstance(payload, dict) or "orderId" not in payload:
            raise ExecutionError("Binance testnet response did not contain an order id; reconcile before retrying")
        return TestnetOrderResult(
            environment="BINANCE_SPOT_TESTNET", symbol=symbol,
            order_id=int(payload["orderId"]), client_order_id=payload.get("clientOrderId"),
            status=str(payload.get("status", "UNKNOWN")), side=side, order_type="LIMIT",
            original_quantity=payload.get("origQty"), price=payload.get("price"), raw_response=payload,
        )


@dataclass(frozen=True, slots=True)
class AlpacaPaperOrderResult:
    environment: str
    order_id: str
    client_order_id: str
    symbol: str
    side: str
    status: str
    quantity: str
    limit_price: str
    order_type: str = "limit"

    def to_dict(self) -> dict:
        from dataclasses import asdict

        return {**asdict(self), "real_money": False}


class AlpacaPaperAdapter:
    """Alpaca US-equity/crypto PAPER endpoint only; no live URL can be configured."""

    BASE_URL = "https://paper-api.alpaca.markets"

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        *,
        timeout: float = 10.0,
        opener: Callable = urllib.request.urlopen,
    ) -> None:
        self.api_key = api_key or os.getenv("ALPACA_PAPER_API_KEY")
        self.api_secret = api_secret or os.getenv("ALPACA_PAPER_SECRET_KEY")
        if not self.api_key or not self.api_secret:
            raise ValueError("set ALPACA_PAPER_API_KEY and ALPACA_PAPER_SECRET_KEY using paper-account credentials")
        if not 1 <= timeout <= 30:
            raise ValueError("timeout must be between 1 and 30 seconds")
        self.timeout = timeout
        self.opener = opener

    def place_limit_order(
        self, *, symbol: str, side: str, quantity: float, limit_price: float,
        time_in_force: str = "day", client_order_id: str | None = None,
    ) -> AlpacaPaperOrderResult:
        symbol = symbol.upper().strip()
        side = side.lower().strip()
        if not re.fullmatch(r"[A-Z0-9./_-]{1,30}", symbol):
            raise ValueError("invalid Alpaca paper symbol")
        if side not in {"buy", "sell"}:
            raise ValueError("side must be buy or sell")
        if not math.isfinite(quantity) or not math.isfinite(limit_price) or quantity <= 0 or limit_price <= 0:
            raise ValueError("quantity and limit_price must be finite and positive")
        if time_in_force not in {"day", "gtc", "ioc", "fok"}:
            raise ValueError("time_in_force must be day, gtc, ioc, or fok")
        if client_order_id is not None and not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", client_order_id):
            raise ValueError("client_order_id must be 1-128 safe characters")
        payload = {
            "symbol": symbol, "qty": format(quantity, ".12g"), "side": side,
            "type": "limit", "limit_price": format(limit_price, ".12g"),
            "time_in_force": time_in_force,
        }
        if client_order_id:
            payload["client_order_id"] = client_order_id
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        request = urllib.request.Request(
            f"{self.BASE_URL}/v2/orders", data=body,
            headers={
                "APCA-API-KEY-ID": self.api_key,
                "APCA-API-SECRET-KEY": self.api_secret,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with self.opener(request, timeout=self.timeout) as response:
                raw = response.read(1_000_001)
        except urllib.error.HTTPError as exc:
            try:
                message = exc.read(4096).decode("utf-8", errors="replace")[:300]
            except OSError:
                message = ""
            raise ExecutionError(f"Alpaca paper endpoint rejected the order (HTTP {exc.code}): {message}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ExecutionError("Alpaca paper transport failed; order status may be unknown, reconcile by client_order_id before retrying") from exc
        if len(raw) > 1_000_000:
            raise ExecutionError("Alpaca paper response exceeded 1 MB")
        try:
            result = json.loads(raw)
            if not isinstance(result, dict):
                raise ValueError("not an object")
            order_id = str(result["id"])
            response_client_id = str(result.get("client_order_id") or client_order_id or "")
            status = str(result["status"])
            returned_qty = str(result.get("qty") or payload["qty"])
            returned_price = str(result.get("limit_price") or payload["limit_price"])
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise ExecutionError("Alpaca paper response was malformed; reconcile by client_order_id before retrying") from exc
        return AlpacaPaperOrderResult(
            environment="ALPACA_PAPER", order_id=order_id,
            client_order_id=response_client_id, symbol=symbol, side=side,
            status=status, quantity=returned_qty, limit_price=returned_price,
        )
