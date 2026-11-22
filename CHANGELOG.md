# Changelog

## 1.0.0 — Final consolidated repository snapshot

- Consolidated 74 original, independently authored trader skill playbooks, 15 specialist agent roles, 13 workflows and 10 skillsets.
- Added opt-in Twelve Data and Binance REST adapters for historical OHLCV and current quote/book snapshots, plus local CSV input.
- Added optional read-only Twelve Data, Binance Spot and Binance USD-M WebSocket price/trade streams with normalized JSONL ticks; reconnect/resubscribe and tick persistence remain operator-level future integrations.
- Added a single-instrument event-time backtesting engine with next-bar-open execution, configurable simple costs, and explicit model limitations.
- Added SQLite persistence, password/session authentication, tenant-scoped paper accounts, transactional append-only application audit events and an optional FastAPI service.
- Added a local cash-equity paper simulator, Alpaca Paper LIMIT-order adapter and Binance Spot Testnet LIMIT-order adapter. No live-money execution adapter is included.
- Added a non-root Docker image, restricted Compose example, Nginx TLS/rate-limiting example and deployment/security documentation.
- Hardened provider redirect validation, request/response bounds, order idempotency, paper-account input validation, and transactional audit coupling.
- Expanded automated tests and release validation; latest local test suite: 121 passed.

This is the final planned feature snapshot for the project brief. It is not a production security certification, regulated trading approval or promise that no future security/maintenance update will ever be required.
