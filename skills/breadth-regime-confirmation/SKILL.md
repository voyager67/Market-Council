---
name: breadth-regime-confirmation
description: "Evaluate market participation, breadth thrusts, deterioration, and benchmark alignment without treating a single breadth statistic as a signal."
domain: market internals
asset_classes: "equities, ETFs, futures"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Breadth and Regime Confirmation

## Purpose

Evaluate market participation, breadth thrusts, deterioration, and benchmark alignment without treating a single breadth statistic as a signal.

## Required inputs

Timestamped advance/decline data; up/down volume; new highs/lows; universe definition; benchmark returns; sector membership; session calendar.

## Procedure

Freeze the eligible universe and timestamp each constituent observation. Reconcile counts, missing constituents, duplicates, and stale symbols. Compute participation ratios and rolling breadth measures with the denominator shown. Compare breadth direction with benchmark price direction and sector concentration. Separate one-day extremes from persistent trends and identify breadth divergences. Record the observation window and conditions that would invalidate the interpretation.

## Expected output

Breadth scorecard with numerator and denominator, universe coverage, participation trend, price/breadth divergences, source timestamps, and unresolved data gaps.

## Guardrails

Never compare breadth series built from different universes or sessions. A breadth thrust is descriptive and is not a standalone entry signal. Do not infer breadth from a single index price.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://github.com/microsoft/qlib
- https://www.sec.gov/data-research/sec-data-resources

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
