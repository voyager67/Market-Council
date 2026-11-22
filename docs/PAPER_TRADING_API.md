# Persistent audit, identity, and paper trading API

## What is implemented

The optional FastAPI service is backed by SQLite and exposes:

- User provisioning through a local CLI command; self-registration is disabled by default and may only be enabled explicitly.
- Password hashes using `hashlib.scrypt`; no plaintext passwords are persisted.
- Random opaque bearer sessions stored as SHA-256 token hashes, with expiry and revocation.
- Per-user audit event queries and append-only audit tables protected by SQLite update/delete triggers.
- Per-user cash-equity paper accounts and deterministic local paper fills.
- Optional external sandbox adapters: Alpaca Paper LIMIT orders and Binance Spot Testnet LIMIT orders. Both adapters use fixed paper/testnet base URLs and return `real_money: false`; there is no live-money endpoint configuration.
- Idempotent `client_order_id` checks, cash-balance validation, long-only sell checks, and average-cost realised P&L calculations.
- Security response headers, trusted-host checks, local-only default binding, and authenticated tenant-scoped account routes.

The local paper broker accepts caller-supplied reference prices. It does not connect to a live broker and does not claim actual market execution. It supports cash-equity long positions only; no margin, shorting, options, futures or crypto positions. External sandbox adapters are distinct: Alpaca Paper submits a LIMIT order using paper-account credentials, and Binance Spot Testnet submits a signed Spot LIMIT order using testnet credentials. Their endpoints are hard-coded and cannot be changed to live/mainnet URLs in this release.

The Alpaca adapter uses the documented paper order endpoint `https://paper-api.alpaca.markets/v2/orders`: <https://docs.alpaca.markets/us/reference/postorder>. The Binance test adapter uses the Spot Testnet only: <https://developers.binance.com/docs/binance-spot-api-docs/testnet>. Use separately issued paper/testnet credentials; never place live credentials in these variables.

## Install and provision

```bash
python -m pip install -e ".[api]"
market-council users create --username trader_one
market-council serve-api --database ./var/marketcouncil.sqlite3
```

The CLI prompts for a password twice; it is not placed in the process argument list. The service binds to `127.0.0.1:8000` by default. `GET /health` is unauthenticated and discloses only a static service status. API docs/OpenAPI are disabled by default.

Set `MC_DATABASE_PATH` to a durable location. Optional settings:

- `MC_ALLOWED_HOSTS`: comma-separated exact hostnames expected from the trusted proxy; default `127.0.0.1,localhost`.
- `MC_ALLOW_SELF_REGISTRATION=1`: enable open trader self-registration. Keep disabled for private deployments unless you have independent abuse prevention.
- `MC_HSTS_ENABLED=1`: emit HSTS only when HTTPS is correctly terminated upstream.
- `MC_ACK_PUBLIC_API_RISK=1`: required by the CLI to bind on a non-loopback host; this is an acknowledgement, not a security control.

## Endpoints

| Method | Route | Authentication | Purpose |
|---|---|---|---|
| GET | `/health` | No | Static health response |
| POST | `/auth/register` | No, disabled by default | Opt-in self-registration |
| POST | `/auth/login` | No | Issue expiring bearer session |
| POST | `/auth/logout` | Bearer | Revoke current session |
| GET | `/me` | Bearer | Current identity |
| GET | `/audit?limit=100` | Bearer | Current user's audit events |
| POST | `/paper/accounts` | Bearer | Create paper account |
| GET | `/paper/accounts/{id}` | Bearer | Read current user's paper account |
| POST | `/paper/accounts/{id}/orders` | Bearer | Simulated market order from supplied reference price |

Example order payload:

```json
{
  "client_order_id": "demo-order-001",
  "symbol": "AAPL",
  "side": "buy",
  "quantity": 5,
  "reference_price": 190.25,
  "fee_bps": 1,
  "slippage_bps": 2
}
```

The response reports `execution_mode: SIMULATED_ONLY` and `real_order_sent: false`. Reusing an idempotency key with a different order payload is rejected.

## External sandbox order adapters

The following commands are intentionally separate from the local API simulator. They submit only to the fixed sandbox endpoints; they do not offer a `--base-url` option. Start with vendor-issued paper/testnet keys and use least privilege.

```bash
# Alpaca Paper LIMIT order only
export ALPACA_PAPER_API_KEY="<paper-account-key>"
export ALPACA_PAPER_SECRET_KEY="<paper-account-secret>"
market-council alpaca-paper-limit --symbol AAPL --side buy --quantity 1 --limit-price 190 --client-order-id mc-demo-001

# Binance Spot Testnet LIMIT order only
export BINANCE_TESTNET_API_KEY="<spot-testnet-key>"
export BINANCE_TESTNET_SECRET="<spot-testnet-secret>"
market-council binance-testnet-limit --symbol BTCUSDT --side BUY --quantity 0.001 --price 50000 --client-order-id mc-test-001
```

The adapters do not poll or reconcile order status after a transport timeout. A timeout or malformed response may mean the remote order status is unknown. Check the official sandbox interface by the submitted client order ID before retrying; do not assume that a timeout means the order was rejected.

## Operational limitations

SQLite is suitable for a local, single-host deployment and modest concurrent usage. Audit inserts are transactionally coupled to registration, login/logout, paper-account creation and local paper-order insertion. SQLite triggers prevent routine application updates/deletes to audit rows; they do not make the file cryptographically tamper-evident or prevent a database administrator from changing the schema/data. SQLite is not a distributed database or high-availability multi-region system. There is no built-in admin console, password reset/MFA, SSO/OIDC, invitation flow, permission matrix, API-key rotation endpoint, rate limiter, tenant encryption key, encrypted-at-rest database, scheduled backup, restore verifier, immutable external audit sink, or regulatory retention workflow. Database backups and access controls are the operator's responsibility.

For public or team deployment, add a TLS-terminating reverse proxy, authentication rate limits, MFA/SSO, invitation/approval provisioning, encrypted storage and backups, monitoring, incident response, penetration testing, and legal/compliance review. Do not expose the application directly to the public internet.
