"""Deterministic cash-equity paper broker backed by SQLite, never a live venue."""

from __future__ import annotations

import math
import re
import sqlite3
import uuid
from dataclasses import asdict, dataclass

from .storage import AuditStore, Database, utc_now


@dataclass(frozen=True, slots=True)
class PaperFill:
    order_id: str
    client_order_id: str
    symbol: str
    side: str
    quantity: float
    reference_price: float
    fill_price: float
    fee: float
    created_at: str
    status: str = "FILLED_SIMULATED"

    def to_dict(self) -> dict:
        return asdict(self)


class PaperBroker:
    """Cash-equity long-only simulator requiring explicit reference prices."""

    def __init__(self, database: Database, *, audit: AuditStore | None = None) -> None:
        self.database = database
        self.audit = audit or AuditStore(database)

    def create_account(self, user_id: str, name: str, initial_cash: float, currency: str = "USD") -> str:
        if not name.strip() or not math.isfinite(initial_cash) or initial_cash < 0:
            raise ValueError("account name is required and initial_cash must be finite and non-negative")
        currency = currency.upper()
        if len(currency) != 3 or not currency.isalpha():
            raise ValueError("currency must be a three-letter code")
        account_id = str(uuid.uuid4())
        with self.database.connect() as conn:
            try:
                conn.execute(
                    "INSERT INTO paper_accounts(id,user_id,name,currency,initial_cash,created_at) VALUES(?,?,?,?,?,?)",
                    (account_id, user_id, name.strip(), currency, initial_cash, utc_now()),
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError("paper account name already exists for this user") from exc
            self.audit.record_in_connection(
                conn, user_id=user_id, action="paper.account_created",
                entity_type="paper_account", entity_id=account_id,
                metadata={"initial_cash": initial_cash, "currency": currency},
            )
        return account_id

    def submit_market_order(
        self, *, user_id: str, account_id: str, client_order_id: str, symbol: str,
        side: str, quantity: float, reference_price: float,
        fee_bps: float = 1.0, slippage_bps: float = 2.0,
    ) -> PaperFill:
        symbol = symbol.upper().strip()
        side = side.lower().strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", client_order_id) or not re.fullmatch(r"[A-Z0-9./_-]{1,30}", symbol):
            raise ValueError("client_order_id or symbol contains unsupported characters")
        numbers = (quantity, reference_price, fee_bps, slippage_bps)
        if not all(math.isfinite(v) for v in numbers) or quantity <= 0 or reference_price <= 0 or fee_bps < 0 or slippage_bps < 0:
            raise ValueError("quantity and reference price must be positive; costs must be finite and non-negative")
        if fee_bps > 5_000 or slippage_bps > 5_000:
            raise ValueError("fee_bps and slippage_bps cannot exceed 5,000")
        if side not in {"buy", "sell"}:
            raise ValueError("side must be buy or sell")
        with self.database.connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            account = conn.execute("SELECT * FROM paper_accounts WHERE id=? AND user_id=?", (account_id, user_id)).fetchone()
            if account is None:
                raise ValueError("paper account not found")
            existing = conn.execute("SELECT * FROM paper_orders WHERE user_id=? AND client_order_id=?", (user_id, client_order_id)).fetchone()
            if existing:
                requested = (account_id, symbol, side, quantity, reference_price)
                original = (existing["account_id"], existing["symbol"], existing["side"], existing["quantity"], existing["reference_price"])
                if requested != original:
                    raise ValueError("client_order_id was already used for a different order")
                return PaperFill(existing["id"], existing["client_order_id"], existing["symbol"], existing["side"], existing["quantity"], existing["reference_price"], existing["executed_price"], existing["fee"], existing["created_at"])
            position_rows = conn.execute(
                "SELECT side,quantity FROM paper_orders WHERE user_id=? AND account_id=? AND symbol=?",
                (user_id, account_id, symbol),
            ).fetchall()
            held = sum(row["quantity"] if row["side"] == "buy" else -row["quantity"] for row in position_rows)
            cash = account["initial_cash"]
            prior_rows = conn.execute(
                "SELECT side,quantity,executed_price,fee FROM paper_orders WHERE user_id=? AND account_id=?",
                (user_id, account_id),
            ).fetchall()
            for row in prior_rows:
                gross = row["quantity"] * row["executed_price"]
                cash += -gross - row["fee"] if row["side"] == "buy" else gross - row["fee"]
            executed = reference_price * (1 + slippage_bps / 10_000) if side == "buy" else reference_price * (1 - slippage_bps / 10_000)
            fee = quantity * executed * fee_bps / 10_000
            if side == "buy":
                if quantity * executed + fee > cash:
                    raise ValueError("insufficient simulated cash")
            elif quantity > held + 1e-12:
                raise ValueError("paper account is long-only; sell quantity exceeds available holdings")
            order_id = str(uuid.uuid4())
            created = utc_now()
            conn.execute(
                "INSERT INTO paper_orders(id,user_id,account_id,client_order_id,symbol,side,quantity,reference_price,executed_price,fee,status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (order_id,user_id,account_id,client_order_id,symbol,side,quantity,reference_price,executed,fee,"FILLED",created),
            )
            self.audit.record_in_connection(
                conn, user_id=user_id, action="paper.order_filled",
                entity_type="paper_order", entity_id=order_id,
                metadata={"symbol": symbol, "side": side, "quantity": quantity,
                          "reference_price": reference_price, "fill_price": executed,
                          "fee": fee, "simulation_only": True},
            )
        return PaperFill(order_id, client_order_id, symbol, side, quantity, reference_price, executed, fee, created)

    def portfolio(self, *, user_id: str, account_id: str) -> dict:
        with self.database.connect() as conn:
            account = conn.execute("SELECT * FROM paper_accounts WHERE id=? AND user_id=?", (account_id, user_id)).fetchone()
            if account is None:
                raise ValueError("paper account not found")
            orders = conn.execute("SELECT symbol,side,quantity,executed_price,fee FROM paper_orders WHERE user_id=? AND account_id=? ORDER BY created_at,id", (user_id, account_id)).fetchall()
        cash = account["initial_cash"]
        positions: dict[str, dict[str, float]] = {}
        realised_pnl = 0.0
        for order in orders:
            gross = order["quantity"] * order["executed_price"]
            cash += -gross - order["fee"] if order["side"] == "buy" else gross - order["fee"]
            item = positions.setdefault(order["symbol"], {"quantity": 0.0, "cost_basis": 0.0, "realised_pnl": 0.0})
            if order["side"] == "buy":
                item["quantity"] += order["quantity"]
                item["cost_basis"] += gross + order["fee"]
            else:
                average_cost = item["cost_basis"] / item["quantity"] if item["quantity"] > 0 else 0.0
                released_basis = average_cost * order["quantity"]
                trade_pnl = gross - order["fee"] - released_basis
                item["quantity"] -= order["quantity"]
                item["cost_basis"] -= released_basis
                item["realised_pnl"] += trade_pnl
                realised_pnl += trade_pnl
        positions = {
            symbol: {
                "quantity": item["quantity"],
                "cost_basis": max(0.0, item["cost_basis"]),
                "average_cost": item["cost_basis"] / item["quantity"] if item["quantity"] > 1e-12 else 0.0,
                "realised_pnl": item["realised_pnl"],
            }
            for symbol, item in positions.items() if abs(item["quantity"]) > 1e-12
        }
        return {"account_id": account_id, "currency": account["currency"], "cash": cash, "positions": positions, "realised_pnl": realised_pnl, "order_count": len(orders), "valuation_note": "Positions are not marked to market. Paper fills are simulated at caller-supplied reference prices plus configured slippage. Realised P&L uses average-cost basis including buy fees and sell fees."}
