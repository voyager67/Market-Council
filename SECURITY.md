# Security Policy

## Supported version

MarketCouncil 1.0.0 is the final planned feature snapshot for this project brief. It is not certified for production trading, account management, brokerage operation or regulated deployment. Security fixes may still be necessary; "final" describes the planned feature scope, not a promise of zero maintenance.

## Reporting a vulnerability

Do not publish API keys, customer datasets, brokerage statements, personal information or exploit details in a public issue. Use the repository host's private vulnerability-reporting feature if enabled, or contact maintainers through a verified private channel.

## Secret handling

- Never commit `.env` files, API keys, access tokens, certificates, SSH private keys, account exports or customer datasets.
- Use a secret manager or protected environment injection; use least-privilege keys.
- Use paper/testnet credentials only with the shipped order adapters.
- Rotate credentials immediately if committed or exposed.
- Review data-retention, processing region and model-training policies before sending market or client data to hosted inference.
- Do not execute untrusted data files or external skill scripts without code review. Bundled skill playbooks are prompt text, not sandboxed code.

## Data and runtime boundary

Market data is retrieved only when the operator explicitly runs the Twelve Data or Binance commands. The implementation includes REST historical-bar and quote adapters, plus optional read-only WebSocket tick/trade streams:

- Twelve Data REST and WebSocket price data for supported instruments and symbols, subject to account entitlement, subscription credits, rate limits and vendor terms.
- Binance public Spot and USD-M crypto-futures REST market data.
- Binance Spot trade and USD-M aggregate-trade WebSocket streams.

WebSocket output is JSONL to stdout. The stream client does not persist ticks, build candles, maintain a full order book, automatically reconnect/resubscribe, recover sequence gaps or trigger trading actions. Provider catalogues, rate limits, market-data delays, subscription entitlements, permitted use and redistribution rights are controlled by each vendor and exchange. No autonomous news/filings fetcher is provided.

The backtesting engine is single-instrument OHLCV with completed-bar signals, next-bar-open fills and simplified basis-point costs. It is not a venue simulator. The internal paper broker is a local long-only cash-equity simulator; external execution adapters are hard-pinned to Alpaca Paper and Binance Spot Testnet and accept LIMIT orders only. No live-money adapter is included.

The optional API includes SQLite persistence, scrypt password hashes, hashed opaque bearer-session tokens, per-user account/audit scoping and append-only audit triggers. Audit events are inserted transactionally with the related user/account/order mutation. SQLite triggers are not a cryptographic or external tamper-proof audit system; database owners can bypass them.

The app defaults to loopback binding and registration disabled. Docker and Nginx deployment examples are provided, but the application does not implement MFA/SSO, password recovery, a permission-admin console, internal rate limiting, external immutable audit storage, encrypted-at-rest database management, backup/restore orchestration, distributed database failover, SIEM or incident response. Do not expose the service publicly without an independently reviewed deployment architecture.

## Production readiness

Local tests exercise interfaces and deterministic fixtures; they do not certify live vendor connectivity, exchange account correctness, fills, strategy performance, privacy controls, threat resistance or regulatory compliance. Run Ruff, Bandit and dependency scans in CI; obtain an independent security review and penetration test; and consult qualified legal/compliance professionals for each jurisdiction and instrument before commercial or customer-facing deployment.
