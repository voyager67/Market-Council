import sqlite3

import pytest

from marketcouncil.auth import AuthManager
from marketcouncil.paper import PaperBroker
from marketcouncil.storage import AuditStore, Database


def setup_user(tmp_path):
    db = Database(tmp_path / "marketcouncil.sqlite3")
    auth = AuthManager(db)
    user = auth.register("trader_one", "long-and-strong-passphrase")
    return db, auth, user


def test_password_hash_login_session_and_revocation(tmp_path):
    _db, auth, user = setup_user(tmp_path)
    with pytest.raises(ValueError, match="invalid username"):
        auth.login("trader_one", "wrong-password")
    session = auth.login("trader_one", "long-and-strong-passphrase")
    assert auth.resolve(session.access_token) == user
    assert auth.logout(session.access_token)
    assert auth.resolve(session.access_token) is None


def test_password_and_username_policy(tmp_path):
    db = Database(tmp_path / "auth.sqlite3")
    auth = AuthManager(db)
    with pytest.raises(ValueError, match="12 and 1024"):
        auth.register("valid_name", "short")
    with pytest.raises(ValueError, match="username"):
        auth.register("x", "long-password-string")


def test_audit_is_append_only_and_tenant_scoped(tmp_path):
    db, _auth, user = setup_user(tmp_path)
    store = AuditStore(db)
    event_id = store.record(user_id=user.id, action="test.event", entity_type="test", entity_id="1", metadata={"ok": True})
    assert store.list_for_user(user.id)[0]["id"] == event_id
    with db.connect() as conn:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            conn.execute("UPDATE audit_events SET action='changed' WHERE id=?", (event_id,))


def test_paper_broker_fills_cash_equity_and_idempotency(tmp_path):
    db, _auth, user = setup_user(tmp_path)
    broker = PaperBroker(db)
    account = broker.create_account(user.id, "Sandbox", 10_000, "USD")
    fill = broker.submit_market_order(
        user_id=user.id, account_id=account, client_order_id="order-1", symbol="AAPL",
        side="buy", quantity=10, reference_price=100, fee_bps=10, slippage_bps=5,
    )
    assert fill.fill_price > 100
    duplicate = broker.submit_market_order(
        user_id=user.id, account_id=account, client_order_id="order-1", symbol="AAPL",
        side="buy", quantity=10, reference_price=100, fee_bps=10, slippage_bps=5,
    )
    assert duplicate.order_id == fill.order_id
    portfolio = broker.portfolio(user_id=user.id, account_id=account)
    assert portfolio["positions"]["AAPL"]["quantity"] == 10
    assert portfolio["order_count"] == 1


def test_paper_broker_rejects_short_sell_and_cross_tenant_reads(tmp_path):
    db, auth, user = setup_user(tmp_path)
    other = auth.register("trader_two", "another-strong-passphrase")
    broker = PaperBroker(db)
    account = broker.create_account(user.id, "Sandbox", 1000)
    with pytest.raises(ValueError, match="long-only"):
        broker.submit_market_order(user_id=user.id, account_id=account, client_order_id="short", symbol="ABC", side="sell", quantity=1, reference_price=10)
    with pytest.raises(ValueError, match="not found"):
        broker.portfolio(user_id=other.id, account_id=account)


def test_paper_broker_prevents_overspending(tmp_path):
    db, _auth, user = setup_user(tmp_path)
    broker = PaperBroker(db)
    account = broker.create_account(user.id, "Small", 10)
    with pytest.raises(ValueError, match="insufficient"):
        broker.submit_market_order(user_id=user.id, account_id=account, client_order_id="too-big", symbol="ABC", side="buy", quantity=2, reference_price=10)


def test_memory_database_and_idempotency_payload_guard(tmp_path):
    memory = Database(":memory:")
    auth = AuthManager(memory)
    user = auth.register("mem_trader", "strong-memory-passphrase")
    assert auth.login("mem_trader", "strong-memory-passphrase").user.id == user.id

    db = Database(tmp_path / "orders.sqlite3")
    user = AuthManager(db).register("order_user", "strong-order-passphrase")
    broker = PaperBroker(db)
    account = broker.create_account(user.id, "Cash", 1000)
    broker.submit_market_order(user_id=user.id, account_id=account, client_order_id="stable-id", symbol="ABC", side="buy", quantity=1, reference_price=10)
    with pytest.raises(ValueError, match="different order"):
        broker.submit_market_order(user_id=user.id, account_id=account, client_order_id="stable-id", symbol="ABC", side="buy", quantity=2, reference_price=10)


def test_duplicate_paper_account_names_are_reported_cleanly(tmp_path):
    db, _auth, user = setup_user(tmp_path)
    broker = PaperBroker(db)
    broker.create_account(user.id, "Default", 1000)
    with pytest.raises(ValueError, match="already exists"):
        broker.create_account(user.id, "Default", 500)


def test_paper_portfolio_average_cost_and_realised_pnl(tmp_path):
    db, _auth, user = setup_user(tmp_path)
    broker = PaperBroker(db)
    account = broker.create_account(user.id, "Accounting", 10_000)
    broker.submit_market_order(user_id=user.id, account_id=account, client_order_id="buy-1", symbol="XYZ", side="buy", quantity=10, reference_price=100, fee_bps=0, slippage_bps=0)
    broker.submit_market_order(user_id=user.id, account_id=account, client_order_id="sell-1", symbol="XYZ", side="sell", quantity=4, reference_price=110, fee_bps=0, slippage_bps=0)
    portfolio = broker.portfolio(user_id=user.id, account_id=account)
    assert portfolio["positions"]["XYZ"]["quantity"] == 6
    assert portfolio["positions"]["XYZ"]["average_cost"] == pytest.approx(100)
    assert portfolio["realised_pnl"] == pytest.approx(40)


def test_registration_and_audit_insert_are_atomic(tmp_path, monkeypatch):
    db = Database(tmp_path / "atomic-auth.sqlite3")
    auth = AuthManager(db)

    def fail_audit(*args, **kwargs):
        raise ValueError("simulated audit write failure")

    monkeypatch.setattr(auth.audit, "record_in_connection", fail_audit)
    with pytest.raises(ValueError, match="audit write failure"):
        auth.register("atomic_user", "a-very-strong-password")
    with db.connect() as conn:
        assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM audit_events").fetchone()[0] == 0


def test_paper_order_and_audit_insert_are_atomic(tmp_path, monkeypatch):
    db, _auth, user = setup_user(tmp_path)
    broker = PaperBroker(db)
    account = broker.create_account(user.id, "Atomic", 1000)

    def fail_audit(*args, **kwargs):
        raise ValueError("simulated audit write failure")

    monkeypatch.setattr(broker.audit, "record_in_connection", fail_audit)
    with pytest.raises(ValueError, match="audit write failure"):
        broker.submit_market_order(
            user_id=user.id, account_id=account, client_order_id="atomic-order",
            symbol="ABC", side="buy", quantity=1, reference_price=10,
        )
    with db.connect() as conn:
        assert conn.execute("SELECT COUNT(*) FROM paper_orders").fetchone()[0] == 0
