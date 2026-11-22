# Trader Workflow Manifests

MarketCouncil ships versioned JSON workflow manifests. Each manifest names its specialist agents, required skills, input contract, decision gates, and intended artifact. The manifests are guidance contracts; the current CLI does not automatically fetch market data or execute the workflow end-to-end.

## Workflows

- [`daily-market-regime`](./daily-market-regime.json) — Daily Market Regime Review
- [`equity-breakout-research`](./equity-breakout-research.json) — Equity Breakout Research
- [`earnings-event-review`](./earnings-event-review.json) — Earnings Event Research
- [`macro-cross-asset-review`](./macro-cross-asset-review.json) — Macro and Cross-Asset Review
- [`options-volatility-review`](./options-volatility-review.json) — Options and Volatility Review
- [`futures-contract-risk`](./futures-contract-risk.json) — Futures Contract and Roll Risk
- [`crypto-market-regime`](./crypto-market-regime.json) — Crypto Market Regime and Venue Review
- [`portfolio-risk-review`](./portfolio-risk-review.json) — Portfolio Exposure and Drawdown Review
- [`systematic-strategy-research`](./systematic-strategy-research.json) — Systematic Strategy Research and Validation
- [`pair-relative-value`](./pair-relative-value.json) — Pair and Relative-Value Research
- [`short-side-risk-review`](./short-side-risk-review.json) — Short-Side and Downside Risk Review
- [`trade-memory-postmortem`](./trade-memory-postmortem.json) — Trade Memory and Performance Postmortem
- [`dividend-quality-review`](./dividend-quality-review.json) — Dividend and Income Equity Review

Every workflow requires human review and fixes `execution_authorization` at `NONE`.
