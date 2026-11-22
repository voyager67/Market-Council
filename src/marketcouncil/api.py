"""Optional FastAPI service for authenticated research audit and paper trading.

Bind to localhost by default. Terminate TLS and apply rate limits at a trusted
reverse proxy before exposing this service to a network.
"""


import os
from pathlib import Path
from typing import Annotated

from .auth import AuthManager, UserIdentity
from .paper import PaperBroker
from .storage import AuditStore, Database


def create_app(database_path: str | Path | None = None):
    try:
        from fastapi import Depends, FastAPI, Header, HTTPException, status
        from fastapi.middleware.trustedhost import TrustedHostMiddleware
        from pydantic import BaseModel, Field
    except ImportError as exc:  # pragma: no cover - optional dependency path
        raise RuntimeError("API extras are optional; install with `pip install -e '.[api]'`") from exc

    db_path = database_path or os.getenv("MC_DATABASE_PATH", "./var/marketcouncil.sqlite3")
    database = Database(db_path)
    audit = AuditStore(database)
    auth = AuthManager(database, audit=audit)
    paper = PaperBroker(database, audit=audit)
    allowed_hosts = [item.strip() for item in os.getenv("MC_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if item.strip()]
    app = FastAPI(title="MarketCouncil API", version="1.0.0", docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
    app.state.database = database
    app.state.auth = auth
    app.state.audit = audit
    app.state.paper = paper

    class RegisterInput(BaseModel):
        username: str = Field(min_length=3, max_length=32)
        password: str = Field(min_length=12, max_length=1024)

    class LoginInput(BaseModel):
        username: str = Field(min_length=3, max_length=32)
        password: str = Field(min_length=1, max_length=1024)

    class AccountInput(BaseModel):
        name: str = Field(min_length=1, max_length=80)
        initial_cash: float = Field(ge=0, allow_inf_nan=False)
        currency: str = Field(default="USD", min_length=3, max_length=3)

    class PaperOrderInput(BaseModel):
        client_order_id: str = Field(min_length=1, max_length=100)
        symbol: str = Field(min_length=1, max_length=50)
        side: str
        quantity: float = Field(gt=0, allow_inf_nan=False)
        reference_price: float = Field(gt=0, allow_inf_nan=False)
        fee_bps: float = Field(default=1, ge=0, le=500, allow_inf_nan=False)
        slippage_bps: float = Field(default=2, ge=0, le=500, allow_inf_nan=False)

    def current_user(authorization: Annotated[str | None, Header()] = None) -> UserIdentity:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
        identity = auth.resolve(authorization[7:].strip())
        if identity is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired session")
        return identity

    @app.middleware("http")
    async def security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        if os.getenv("MC_HSTS_ENABLED", "0") == "1":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    @app.get("/health")
    def health():
        return {"status": "ok", "mode": "paper-and-research-only"}

    @app.post("/auth/register", status_code=201)
    def register(payload: RegisterInput):
        if os.getenv("MC_ALLOW_SELF_REGISTRATION", "0") != "1":
            raise HTTPException(status_code=403, detail="self-registration is disabled; provision users through the CLI")
        try:
            user = auth.register(payload.username, payload.password)
            return {"id": user.id, "username": user.username, "role": user.role}
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.post("/auth/login")
    def login(payload: LoginInput):
        try:
            session = auth.login(payload.username, payload.password)
        except ValueError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        return {"access_token": session.access_token, "token_type": session.token_type, "expires_at": session.expires_at, "user": {"id": session.user.id, "username": session.user.username, "role": session.user.role}}

    @app.post("/auth/logout")
    def logout(user: Annotated[UserIdentity, Depends(current_user)], authorization: Annotated[str | None, Header()] = None):
        token = authorization[7:].strip() if authorization else ""
        auth.logout(token)
        return {"status": "logged_out"}

    @app.get("/me")
    def me(user: Annotated[UserIdentity, Depends(current_user)]):
        return {"id": user.id, "username": user.username, "role": user.role}

    @app.get("/audit")
    def list_audit(user: Annotated[UserIdentity, Depends(current_user)], limit: int = 100):
        try:
            return {"events": audit.list_for_user(user.id, limit)}
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/paper/accounts", status_code=201)
    def create_paper_account(payload: AccountInput, user: Annotated[UserIdentity, Depends(current_user)]):
        try:
            account_id = paper.create_account(user.id, payload.name, payload.initial_cash, payload.currency)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return {"account_id": account_id, "mode": "PAPER_ONLY"}

    @app.get("/paper/accounts/{account_id}")
    def get_paper_account(account_id: str, user: Annotated[UserIdentity, Depends(current_user)]):
        try:
            return paper.portfolio(user_id=user.id, account_id=account_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/paper/accounts/{account_id}/orders", status_code=201)
    def place_paper_order(account_id: str, payload: PaperOrderInput, user: Annotated[UserIdentity, Depends(current_user)]):
        try:
            fill = paper.submit_market_order(
                user_id=user.id, account_id=account_id,
                client_order_id=payload.client_order_id, symbol=payload.symbol,
                side=payload.side, quantity=payload.quantity,
                reference_price=payload.reference_price,
                fee_bps=payload.fee_bps, slippage_bps=payload.slippage_bps,
            )
        except ValueError as exc:
            status_code = 404 if "not found" in str(exc) else 422
            raise HTTPException(status_code=status_code, detail=str(exc)) from exc
        return {**fill.to_dict(), "execution_mode": "SIMULATED_ONLY", "real_order_sent": False}

    return app
