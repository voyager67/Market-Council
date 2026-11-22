---
name: futures-contract-sizing
description: "Translate futures price risk into contract-level currency exposure using verified contract multipliers, tick values, expiry, and margin assumptions."
domain: derivatives risk
asset_classes: "futures"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Futures Contract Risk and Sizing

## Purpose

Translate futures price risk into contract-level currency exposure using verified contract multipliers, tick values, expiry, and margin assumptions.

## Required inputs

Exchange contract specification; contract month; multiplier; tick size/value; entry and stop; account equity; currency; fees/slippage; FX conversion.

## Procedure

Confirm exact venue, product code, contract month, and deliverable/settlement type. Verify multiplier, tick size, tick value, and currency from exchange documentation. Calculate per-contract stop loss and currency conversion separately. Compare risk-budget units with margin and liquidity constraints. Model gap, limit move, roll, expiry, and basis risks. Report rounded contract counts and assumptions for a separate human check.

## Expected output

Contract sizing worksheet with specification source, tick economics, stop-loss estimate, margin notes, FX conversion, and stress cases.

## Guardrails

Do not reuse contract specifications across venues or expiries. Margin is not maximum loss. Reject sizing if multipliers or tick values are unknown.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://nautilustrader.io/docs/latest/concepts/overview/
- https://www.quantconnect.com/docs/v2/lean-engine/getting-started

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
