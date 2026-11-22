import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from marketcouncil.api import create_app


def test_authenticated_api_paper_flow_is_tenant_scoped(tmp_path, monkeypatch):
    monkeypatch.setenv("MC_ALLOW_SELF_REGISTRATION", "1")
    app = create_app(tmp_path / "api.sqlite3")
    client = TestClient(app, base_url="http://localhost")
    assert client.get("/health").status_code == 200
    assert client.get("/me").status_code == 401
    registered = client.post("/auth/register", json={"username": "api_trader", "password": "long-secure-passphrase"})
    assert registered.status_code == 201
    login = client.post("/auth/login", json={"username": "api_trader", "password": "long-secure-passphrase"})
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    account = client.post("/paper/accounts", headers=headers, json={"name": "Test", "initial_cash": 10000, "currency": "USD"})
    assert account.status_code == 201
    account_id = account.json()["account_id"]
    order = client.post(f"/paper/accounts/{account_id}/orders", headers=headers, json={"client_order_id": "api-1", "symbol": "MSFT", "side": "buy", "quantity": 2, "reference_price": 50})
    assert order.status_code == 201
    assert order.json()["real_order_sent"] is False
    assert order.json()["execution_mode"] == "SIMULATED_ONLY"
    portfolio = client.get(f"/paper/accounts/{account_id}", headers=headers)
    assert portfolio.json()["positions"]["MSFT"]["quantity"] == 2
    audit = client.get("/audit", headers=headers)
    assert audit.status_code == 200 and len(audit.json()["events"]) >= 4
    assert "X-Content-Type-Options" in portfolio.headers
    assert client.post("/auth/logout", headers=headers).status_code == 200
    assert client.get("/me", headers=headers).status_code == 401


def test_api_registration_disabled_by_default(tmp_path, monkeypatch):
    monkeypatch.delenv("MC_ALLOW_SELF_REGISTRATION", raising=False)
    client = TestClient(create_app(tmp_path / "closed.sqlite3"), base_url="http://localhost")
    response = client.post("/auth/register", json={"username": "new_trader", "password": "long-secure-passphrase"})
    assert response.status_code == 403


def test_api_tenant_cannot_read_another_users_paper_account(tmp_path, monkeypatch):
    monkeypatch.setenv("MC_ALLOW_SELF_REGISTRATION", "1")
    client = TestClient(create_app(tmp_path / "tenants.sqlite3"), base_url="http://localhost")
    sessions = []
    for username, password in (("first_user", "first-secure-passphrase"), ("second_user", "second-secure-passphrase")):
        assert client.post("/auth/register", json={"username": username, "password": password}).status_code == 201
        token = client.post("/auth/login", json={"username": username, "password": password}).json()["access_token"]
        sessions.append({"Authorization": f"Bearer {token}"})
    account = client.post("/paper/accounts", headers=sessions[0], json={"name": "Private", "initial_cash": 1000}).json()["account_id"]
    assert client.get(f"/paper/accounts/{account}", headers=sessions[1]).status_code == 404
