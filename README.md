> **Repository import status:** The GitHub repository has been initialized and this landing README is committed. The complete 1.0.0 source tree has **not** yet been imported. This repository is not a complete runnable release until the contents of the final source ZIP are extracted into the repository root and committed. The ZIP contains the complete README with images/video and all source assets; copying its `market-council/` contents into this repository will replace this temporary notice.

# MarketCouncil

> **One Market. Fifteen Specialists. No Unchallenged Thesis.**

**The multi-agent research workbench for serious traders, portfolio managers and quantitative researchers.**

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Version](https://img.shields.io/badge/Version-1.0.0-1F9D8B)
![License](https://img.shields.io/badge/License-MIT-2E8B57)
![Agents](https://img.shields.io/badge/Agent%20roles-15-4567A7)
![Skills](https://img.shields.io/badge/Trader%20skills-74-148F77)
![Workflows](https://img.shields.io/badge/Workflows-13-7956A8)
![Skillsets](https://img.shields.io/badge/Skillsets-10-7956A8)

> **Not another AI signal bot. Your trading research desk, rebuilt as a specialist council.**

MarketCouncil coordinates specialist AI agents to examine market questions from different angles, challenge assumptions, expose missing evidence and produce structured research briefs. It combines **15 agent roles**, **74 trader-focused skill playbooks**, **13 operational workflows** and **10 skillsets** in a Python project.

The core principle is simple: AI helps organise and challenge research. It does not own the trade, guarantee a fill, or authorise live execution.

## Why MarketCouncil

Professional trading research spans market structure, fundamentals, catalysts, macro conditions, positioning, derivatives, liquidity and portfolio risk. MarketCouncil makes those perspectives explicit:

- **Specialists, not one generic prompt:** agents receive assigned domain skill playbooks and return structured findings.
- **Bull/bear challenge:** opposing researchers build conditional cases and identify invalidation criteria.
- **Synthesis after analysis:** the director reconciles disagreement, confidence and data gaps.
- **Deterministic risk utilities:** position sizing and hard constraints are calculated in code, not delegated to an LLM.
- **Provider flexibility:** route roles to compatible hosted or local models.
- **Human decision boundary:** reports are research artefacts, not buy/sell instructions.

## The research council

| Layer | Roles |
|---|---|
| Market and security research | Technical Analyst, Fundamental Analyst, Macro Strategist, Catalyst Researcher, Sentiment Analyst, Quant Researcher |
| Instruments and market structure | Microstructure Analyst, Derivatives Analyst, Crypto Analyst, Earnings Analyst, Institutional Flow Analyst |
| Portfolio and risk | Portfolio Risk Officer |
| Adversarial review | Bull Researcher, Bear Researcher |
| Final synthesis | Synthesis Director |

Domain analysts and bull/bear reviewers can run concurrently within a configurable worker limit. The synthesis director runs after specialist reports are collected. This is orchestrated role separation—not proof that model outputs are independent or correct.

## 74 trader skills · 13 workflows · 10 skillsets

The skill library covers technical analysis and market internals; equity fundamentals and screening; macro, FX and positioning; options, futures and digital assets; quantitative and relative-value research; portfolio and risk management; and trader journaling, postmortems and research governance.

Workflows define ordered skill sequences, inputs, outputs and human decision gates. Skillsets group capabilities by trader objective. See `skills/`, `workflows/`, `skillsets/`, and `skills-index.json` in the complete source distribution.

## Market data, backtesting and paper trading

| Capability | Included implementation | Boundary |
|---|---|---|
| Twelve Data | REST historical bars, quote snapshots and optional WebSocket price ticks | Symbols, instruments, credits and limits depend on subscription |
| Binance | Public Spot and USD-M crypto-futures market data; Spot trade and USD-M aggregate-trade streams | Crypto market-data connectors, not universal equities/FX/futures feeds |
| Local CSV | Validated OHLCV inputs | Operator owns data quality, timestamps, adjustments and provenance |
| Historical backtesting | Inspectable single-instrument OHLCV engine; completed-bar signal and next-bar-open fill assumptions | Simplified costs; not an exchange-grade simulator |
| Local paper simulator | SQLite-backed long-only cash-equity simulation | Caller-supplied reference prices |
| External sandbox | Alpaca Paper and Binance Spot Testnet LIMIT adapters | Test environments only; no live-money adapter |

WebSocket streams are read-only JSONL. Automatic reconnect/resubscribe, sequence-gap recovery, persistent tick storage, candle construction and provider failover are not implemented. The backtester does not model order-book queue priority, market impact, corporate actions, delistings, borrow, funding, margin/liquidation, options or multi-asset portfolio interactions.

## Multi-model AI

Install the optional LiteLLM adapter:

```bash
python -m pip install -e ".[ai]"
export MC_PROVIDER=litellm
export MC_MODEL='openai/<model-id>'
export OPENAI_API_KEY='<load-from-secret-manager>'
```

Per-role model routing is supported through `MC_AGENT_MODELS`. Provider/model support, structured-output behaviour, rate limits, retention, region and data-use terms must be checked for each provider. Hosted inference transmits prompts and supplied context to that provider; do not send confidential customer or trading data without authorisation.

## Audit, authentication and API

The optional API provides SQLite-backed users, password hashes, hashed opaque sessions, tenant-scoped paper accounts/orders and transactional audit-event insertion. Self-registration is disabled by default.

It is not a complete enterprise identity platform. MFA/SSO, password recovery, internal rate limiting, external immutable audit storage, distributed failover and a full admin permission console are not included.

## Quick start

**Requirements:** Python 3.11+. AI, API, WebSocket and development dependencies are optional extras.

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e .

market-council skills validate
market-council workflows validate
market-council demo --format markdown
```

The deterministic offline demo requires no market-data API key or hosted AI credential.

### Analyse a CSV

```bash
market-council analyze \
  --csv ./data/instrument.csv \
  --symbol YOUR-SYMBOL \
  --timeframe 1d \
  --bars-per-year 252 \
  --question "Review the setup, key risks and missing evidence" \
  --provider mock \
  --format markdown
```

### Run a backtest

```bash
market-council backtest --csv ./data/AAPL.csv --fast 10 --slow 30 \
  --initial-equity 100000 --commission-bps 5 --slippage-bps 5 --bars-per-year 252
```

### Deterministic position sizing

```bash
market-council size --equity 100000 --risk-pct 0.5 \
  --entry 100 --stop 97 --side long --max-position-pct 20
```

Sizing is a linear per-unit estimate. It does not replace instrument-specific multipliers, lot sizes, margin, Greeks, borrow, funding, taxes, gaps, market impact or portfolio correlation. Stops do not guarantee maximum loss.

## Security and risk boundaries

MarketCouncil is **not production-certified** for brokerage, customer-account management, regulated financial services or unattended trading. Before exposing the API or using customer data, obtain independent security review and penetration testing; configure TLS, secrets, backups, monitoring, rate limits, incident response and access controls; and obtain jurisdiction-specific legal/compliance advice.

The project does not independently verify every market-data source or model claim. Backtest results can be invalidated by look-ahead bias, survivorship bias, bad timestamps, corporate actions, unrealistic fills and regime changes.

**No live-money order adapter is included. Never treat an AI report, model consensus, backtest or sizing calculation as a trade instruction.**

## Verification

The prepared source snapshot recorded **121 passing tests**, successful repository/skill/workflow validation and an offline 15-agent demo with `HUMAN_REVIEW_REQUIRED` and `execution_authorization: NONE`.

Ruff, Bandit and pip-audit were not run in the preparation environment because the tools were unavailable offline. Run them in CI before treating the project as release-cleared:

```bash
ruff check .
pytest -q
bandit -q -r src/marketcouncil
pip-audit
```

## Project layout

- `src/marketcouncil/` — runtime, agents, providers, data, streams, backtest, risk, storage, auth, API and paper adapters
- `skills/` — 74 trader playbooks
- `workflows/` — 13 workflow manifests
- `skillsets/` — 10 trader bundles
- `tests/` — deterministic unit and contract tests
- `docs/` — architecture, operating model, integrations, deployment and risk
- `assets/` — original SVG/PNG/GIF/MP4 product illustrations
- `deploy/` — Docker Compose and Nginx examples

## License

MIT. See `LICENSE` and `PROVENANCE.md` for terms and implementation/research provenance.

---

**MarketCouncil 1.0.0 — final consolidated feature scope.** "Final" means the planned feature scope is consolidated; it does not mean maintenance, dependency updates or security fixes will never be needed.
