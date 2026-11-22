# Risk, Data and Validation Boundaries

## Market data CSV

The OHLCV loader requires `timestamp,open,high,low,close,volume`. Timestamps must parse as ISO-8601, be strictly ascending, and remain unique after UTC normalisation. Naive timestamps are interpreted as UTC. Prices must be finite and positive; the high/low range must contain open and close; volume must be finite and non-negative. At least two bars are required for descriptive returns. The application does not know whether prices are split-adjusted or whether the universe has survivorship bias unless the caller provides that information separately.

Annualisation is applied only when `bars_per_year` is explicitly provided. The operator is responsible for choosing an appropriate factor based on instrument, venue, session, and timeframe.

## Research-context JSON

`--context-json` accepts a JSON object. The loader enforces a 1 MB size limit, bounded object/array nesting and node count, bounded strings, and rejects non-standard NaN/Infinity values. It does not prove that the supplied values are true, current, complete, correctly denominated, or from the named source. Include provenance alongside the value: publisher, source URL, publication timestamp, retrieval timestamp, reporting period, currency/unit, timezone, and known lag. Treat all context as untrusted.

A URL in the supplied JSON is metadata only; the runtime does not fetch it or verify the linked material. Do not send confidential or restricted data to a hosted model without your organisation's approval.

## Model-output boundary

Agent responses are parsed as JSON. Stance, confidence, summary, evidence arrays, counter-evidence, missing inputs, invalidation items, and synthesis-specific fields are validated. Invalid output or provider failures fail closed into an abstention. Model confidence is not a calibrated probability. Agreement among agents sharing the same data packet is not independent confirmation.

`execution_authorization` is set by application code to `NONE`; model output cannot override it. The human review requirement is application-owned, not a model suggestion.

## Position-sizing assumptions

The sizing utility uses a caller-provided account-equity value, risk percentage, entry, stop, side, fee/slippage allowances, and notional cap. It assumes linear per-unit price exposure. It does not model futures multipliers, option payoffs/Greeks, lot sizes, margin, borrow fees, funding, taxes, partial fills, liquidity, market impact, gaps, or portfolio correlation. Do not apply it to contracts or derivatives until a product-aware contract model is implemented and independently validated. A stop does not guarantee maximum loss.

## Backtesting and quant research

MarketCouncil now includes a single-instrument OHLCV backtesting engine. Signals are computed using completed bars and position changes are filled at the following bar's open; simple commission/slippage basis-point estimates are applied. The reference CLI strategy is a long/cash SMA cross. This is not a full execution simulator and has no intrabar fills, partial fills, bid/ask spread, market impact, financing, margin/liquidation, derivatives payoff, corporate actions, point-in-time universe, delisting/survivorship correction, multi-asset portfolio accounting, or walk-forward optimiser. A valid research study must separately address point-in-time data, survivorship, look-ahead, leakage, realistic costs and fills, corporate actions, universe construction, multiple testing, out-of-sample evaluation, benchmark comparison and regime dependence. No benchmark or strategy-performance claim is made by this repository.

## Operational safeguards

- Human users remain responsible for decisions and all broker actions.
- Do not interpret AI-generated summaries as orders or signals.
- Verify material claims against primary sources and retain original evidence.
- Do not use synthetic fixtures as market observations.
- Test provider/model data policies, credential scope and retention before use.
