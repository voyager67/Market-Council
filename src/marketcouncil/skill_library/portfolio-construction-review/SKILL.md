---
name: portfolio-construction-review
description: "Review portfolio construction, diversification, factor overlap, liquidity, currency exposure, and scenario concentration using trader-supplied holdings."
domain: portfolio management
asset_classes: "multi-asset"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Portfolio Construction and Concentration Review

## Purpose

Review portfolio construction, diversification, factor overlap, liquidity, currency exposure, and scenario concentration using trader-supplied holdings.

## Required inputs

Timestamped holdings; instrument identifiers; market values; cash; currency; sector/factor tags; benchmark; portfolio constraints.

## Procedure

Reconcile holdings totals, duplicate identifiers, cash, and stale marks. Normalize asset class, currency, sector, and instrument exposure. Measure single-name, sector, factor, issuer, venue, and currency concentrations where data supports it. Examine correlated risk under declared scenarios rather than assuming historical correlations are stable. Compare allocations with trader policy limits. Produce exceptions and required human decisions, not automatic rebalance orders.

## Expected output

Portfolio exposure map with reconciliation status, concentrations, scenario sensitivities, policy exceptions, and human review items.

## Guardrails

Do not infer suitability, risk tolerance, or target allocation. Correlation is regime-dependent and does not guarantee diversification during stress.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://nautilustrader.io/docs/latest/concepts/overview/
- https://github.com/microsoft/qlib

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
