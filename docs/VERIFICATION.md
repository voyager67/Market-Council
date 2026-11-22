# Verification Record — MarketCouncil 1.0.0

This record describes local verification of the current repository snapshot. It is not a production certification, provider interoperability certification, data-quality attestation, compliance approval, security audit, or evaluation of trading returns. Update counts only after rerunning the commands below.

## Repository scope

- **121 automated tests passed** in the latest local source-tree test run.
- **74 portable trader skills**, mirrored in the runtime package and all mapped to at least one specialist role.
- 15 agent roles (12 domain specialists, bull and bear researchers, and a synthesis director).
- 13 workflow manifests and 10 skillsets.
- REST market data: Twelve Data (equities, FX, crypto and selected futures subject to account entitlement) and Binance public Spot/USD-M crypto-futures data; local CSV input remains available.
- WebSocket market data: Twelve Data price ticks for entitled symbols; Binance Spot trade and USD-M aggregate-trade streams. Output is JSONL only; stream recovery and tick persistence are not included.
- Backtest: single-instrument OHLCV, completed-bar signal and next-bar-open fill model, with simplified costs.
- Paper/execution: local SQLite cash-equity simulator, Alpaca Paper LIMIT orders and Binance Spot Testnet LIMIT orders. No live-money adapter.
- Persistence/API: SQLite user/session/audit/paper records and optional FastAPI service with tenant-scoped routes.
- Deployment: non-root Docker image, restricted Compose example and Nginx TLS/rate-limiting example.

## Reproducible checks

```bash
python scripts/validate_repository.py
python scripts/build_skill_index.py --check
python scripts/build_skill_catalog.py --check
python -m compileall -q src tests scripts
pytest -q
ruff check .
bandit -q -r src/marketcouncil
pip-audit
market-council skills validate
market-council workflows validate
market-council demo --format json
```

The local checks cover schema contracts, source/package mirrors, skill-to-agent routing, workflow and skillset references, local Markdown links, secret-pattern scanning, CSV/context validation, provider response parsing and redirect rejection, backtest timing/cost boundaries, atomic audit writes, authentication/session expiry and revocation, tenant isolation, local paper trading, sandbox order signatures and API route behaviour. The latest deterministic test output was `121 passed`.

## Not verified locally

- Ruff lint was not run because the executable was unavailable in the offline environment. CI includes Ruff.
- Bandit and pip-audit results must be checked in the hosted CI environment if those tools are unavailable locally.
- Docker image build, Nginx configuration validation, host-level TLS, secrets manager, backup/restore, firewall, monitoring and incident-response setup were not exercised in this container.
- Twelve Data, Binance, Alpaca Paper, hosted AI provider, and any real account credentials or rate-limit entitlements were not exercised against the live external services. Provider tests use controlled fixtures.
- Live provider connections were not exercised against external vendor accounts; native WebSocket message parsing, subscription failure handling and CLI wiring are covered by offline fixtures. Automatic reconnect/resubscribe, sequence-gap recovery, persistent tick storage, live news/filings/calendar ingestion and provider failover are not implemented.
- Backtest profitability, alpha, statistical power, strategy robustness, fill quality, margin, corporate-action or survivorship correctness.
- Independent security audit, penetration test, privacy review, regulatory assessment, and jurisdiction-specific compliance approval.

The offline demo uses synthetic fixture data and a deterministic mock provider. Its output is not a forecast or trading recommendation. Sandbox adapters are endpoint-pinned, but they still require careful human review and vendor-issued sandbox credentials.
