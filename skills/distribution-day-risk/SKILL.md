---
name: distribution-day-risk
description: "Review potential distribution clusters, failed rallies, and market-top conditions using predeclared definitions and multiple confirming measures."
domain: market risk
asset_classes: "equities, ETFs"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Distribution and Market-Top Risk Review

## Purpose

Review potential distribution clusters, failed rallies, and market-top conditions using predeclared definitions and multiple confirming measures.

## Required inputs

Benchmark OHLCV; volume baseline; session calendar; breadth; distribution-day definition; historical regime labels if available.

## Procedure

Declare price-change and relative-volume thresholds before scanning. Confirm adjusted, complete benchmark bars and session alignment. Identify qualifying sessions and expiry rules. Review clusters, follow-through, failed rallies, and breadth confirmation. Run sensitivity checks around thresholds and compare alternate benchmarks. Report the observation as a risk condition, not a directional prediction.

## Expected output

Distribution-risk ledger with qualifying sessions, rule parameters, cluster state, sensitivity, corroborating evidence, and invalidation conditions.

## Guardrails

Do not imply a market top from a fixed count alone. Do not import thresholds from a methodology without disclosing that they are chosen heuristics.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://docs.freqtrade.io/en/latest/backtesting/
- https://github.com/microsoft/qlib

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
