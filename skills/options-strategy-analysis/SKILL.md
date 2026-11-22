---
name: options-strategy-analysis
description: "Compare option structures through payoff, Greeks, volatility surface, liquidity, expiry, assignment, and scenario analysis."
domain: options research
asset_classes: "options, equities, ETFs, futures options"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Options Strategy and Volatility Analysis

## Purpose

Compare option structures through payoff, Greeks, volatility surface, liquidity, expiry, assignment, and scenario analysis.

## Required inputs

Underlying and option chain timestamp; expiry; strike; call/put; bid/ask; contract multiplier; rates/dividends; implied volatility; Greeks; exercise style.

## Procedure

Verify contract identity, multiplier, expiry, settlement, and exercise style. Inspect bid/ask quality, open interest, volume, and stale quotes. Decompose payoff and Greeks by leg and across underlying/volatility/time scenarios. Compare implied and historical volatility only over aligned horizons. Include early assignment, pin, exercise, gap, and liquidity effects. Present max loss/profit only where structurally defined and identify model assumptions.

## Expected output

Options strategy comparison with legs, payoff boundaries, Greeks, volatility assumptions, liquidity, scenario table, and event/assignment risks.

## Guardrails

Greeks are local sensitivities, not guarantees. Do not quote a theoretical price as executable. Do not present a complex spread as limited-risk unless all legs and exercise mechanics support it.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://www.optionseducation.org/theoptionseducationcenter/learning-resources-by-topic/greeks-and-volatility
- https://prd-web.optionseducation.org/advancedconcepts/understanding-options-greeks

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
