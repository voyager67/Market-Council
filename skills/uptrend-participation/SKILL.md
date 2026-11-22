---
name: uptrend-participation
description: "Measure how broadly instruments satisfy a declared trend template and whether participation is expanding or contracting."
domain: trend participation
asset_classes: "equities, ETFs"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Uptrend Participation Analysis

## Purpose

Measure how broadly instruments satisfy a declared trend template and whether participation is expanding or contracting.

## Required inputs

Point-in-time constituent universe; adjusted OHLCV; moving-average definitions; benchmark series; lookback windows; corporate-action policy.

## Procedure

State the exact trend template and parameter values before calculation. Verify adjusted-price consistency and point-in-time membership. Compute per-instrument trend states using only data available at each timestamp. Aggregate eligible, improving, deteriorating, and unclassified counts. Report sector and market-cap concentration to expose narrow index leadership. Compare rolling participation with benchmark direction and note missing-data sensitivity.

## Expected output

Trend-participation cohort table with exact rules, coverage, concentration, and interpretation limits.

## Guardrails

Do not alter thresholds after seeing outcomes without marking the work exploratory. Do not backfill current constituents into historical universes.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://github.com/microsoft/qlib
- https://docs.freqtrade.io/en/latest/backtesting/

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
