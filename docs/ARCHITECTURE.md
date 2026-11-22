# MarketCouncil 1.0.0 Architecture

## Runtime surfaces

1. **Market data:** `TwelveDataProvider` retrieves supported historical bars and quote snapshots for equities, FX, crypto and selected futures/instruments subject to provider catalogue and subscription entitlements. `BinanceKlinesProvider` retrieves public Spot crypto and USD-M crypto-futures bars and best-bid/ask snapshots. `CSVMarketDataProvider` handles local OHLCV. HTTP requests are HTTPS-only, provider-host-allowlisted, time-bounded and response-size-bounded; final redirect hosts are checked.
2. **Validation and research:** timestamped OHLCV and bounded research-context JSON are validated. The research-context packet is caller-supplied and is not automatically verified against its referenced sources.
3. **Specialist council:** 12 domain analysts and two adversarial analysts (bull and bear) run concurrently through a bounded thread pool. Each role receives mapped `SKILL.md` playbooks.
4. **Synthesis:** the synthesis director runs after upstream reports are collected and preserves disagreement, uncertainty and missing evidence.
5. **Backtesting and risk:** deterministic Python includes a single-instrument event-time OHLCV backtester (completed-bar signal, next-bar-open execution) and a separate linear position-size calculator. Neither is a portfolio margin or venue-matching simulator.
6. **Persistence and paper execution:** SQLite stores users, expiring sessions, tenant-scoped paper accounts/orders and append-only audit events. Authentication, paper orders and their audit inserts are committed in the same transaction. A local cash-equity simulator and external Alpaca Paper / Binance Spot Testnet LIMIT-only adapters are available.
7. **API and deployment:** optional FastAPI endpoints provide authenticated user-scoped audit and paper-account operations. Docker, restricted Compose and Nginx TLS/rate-limit examples are included.

## Agent roster

**Market and security analysis:** `technical_analyst`, `fundamental_analyst`, `macro_strategist`, `catalyst_researcher`, `sentiment_analyst`, `quant_researcher`.

**Instrument and market structure analysis:** `microstructure_analyst`, `derivatives_analyst`, `crypto_analyst`, `earnings_analyst`, `institutional_flow_analyst`.

**Risk, challenge and synthesis:** `portfolio_risk_officer`, `bull_researcher`, `bear_researcher`, `synthesis_director`.

The 12 domain specialists and bull/bear analysts run concurrently; synthesis runs after them. Fifteen agent roles do not imply fifteen separate model instances: the operator can map roles to the same or different provider/model identifiers.

## Skill system and operational manifests

The 74 portable playbooks are duplicated intentionally: `skills/<id>/SKILL.md` is the runtime-independent repository surface, while `src/marketcouncil/skill_library/<id>/SKILL.md` is packaged with the Python distribution. `skills-index.json` is canonical metadata; the validator checks it against the source playbooks. Every skill maps to at least one role. Skills are prompt guidance, not sandboxed executable code.

`workflows/*.json` defines trader workflows, inputs, agent roles, skill references, output artifacts and human decision gates. `skillsets/*.json` groups capabilities by trader persona or instrument class. The CLI validates these manifests; it does not automatically execute every step as an autonomous workflow.

## Provider and data boundary

`LLMProvider` defines the inference boundary. `MockProvider` supports deterministic offline tests; `LiteLLMProvider` is optional. Live market-data adapters are explicit opt-in REST and WebSocket clients for Twelve Data and Binance public market data. WebSocket streams normalize price/trade ticks and emit JSONL to stdout; they do not persist ticks. Real-time coverage, exchange availability, data delays, symbol catalogue and redistribution terms depend on provider and account. Automatic stream recovery/resubscription, sequence-gap recovery, provider failover, corporate-action adjustment and broad real-time news/filings/calendar ingestion are not included.

## Backtesting boundary

The engine is single-instrument OHLCV, with signals calculated from completed bars and position changes at the next bar open. It supports a simple strategy protocol and an SMA-cross reference strategy, costs as basis-point assumptions, and basic return/drawdown/exposure metrics. It does not model partial fills, intrabar order types, bid/ask spread, queue priority, impact, margin/liquidation, borrow/funding, derivatives payoff, corporate actions, survivorship, point-in-time universes or walk-forward optimisation. Results are not performance claims.

## Persistence, authentication and execution boundary

SQLite persists user credentials as scrypt hashes, stores only hashes of opaque bearer-session tokens, and scopes paper accounts and audit queries by user ID. Audit rows are append-only through database triggers and are inserted in the same transaction as authentication/account/order mutations. This is an application-level append-only control, not a cryptographically tamper-evident external ledger: a database administrator can alter the database or schema.

The internal paper simulator is cash-equity long-only and uses caller-supplied reference prices. External adapters are fixed to `https://paper-api.alpaca.markets` and `https://testnet.binance.vision`; both are LIMIT-only in this release. No mainnet/live-money execution adapter exists. A transport timeout can leave an order's remote status unknown and requires reconciliation at the venue before retry.

## Security and production limitations

Research context is treated as untrusted data; it is not independently source-verified. The API defaults to loopback binding, disables self-registration by default, uses scrypt password hashes, expiring opaque bearer sessions, trusted-host checks and response security headers. Nginx examples show TLS termination and authentication rate limits; Docker examples use a non-root user, read-only root filesystem, limited capabilities and a persistent data volume.

This is not a production security certification. Missing controls include built-in MFA/SSO, password reset and recovery, formal role/permission administration, rate limiting inside the app, external immutable audit sink, encrypted database/backup lifecycle, distributed database and high availability, automated monitoring/incident management, independent penetration testing, regulatory approval and jurisdiction-specific compliance workflows. Operators must add and validate these before real users or sensitive data are onboarded.

## Explicit non-features

No live-money order execution, automatic WebSocket stream recovery/resubscription, persistent tick storage, automatic news/filings/calendar aggregation, automated citation verification, broad multi-asset portfolio backtesting, venue-grade execution simulation, margin/derivatives ledger, autonomous strategy optimiser, MCP server or dashboard is included. Workflow manifests remain human-reviewed operational blueprints.
