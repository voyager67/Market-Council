---
name: earnings-reaction-study
description: "Study post-earnings price reactions and potential drift while controlling event selection, benchmark moves, and transaction-cost assumptions."
domain: event-driven research
asset_classes: "equities, options"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Earnings Reaction and Drift Study

## Purpose

Study post-earnings price reactions and potential drift while controlling event selection, benchmark moves, and transaction-cost assumptions.

## Required inputs

Timestamped earnings release; estimates source and vintage; adjusted price data; event calendar; benchmark; sector index; fees and slippage.

## Procedure

Freeze the eligible event universe and release timestamps. Calculate surprise only when actual and consensus values share a consistent definition and vintage. Compute event returns in consistent sessions relative to benchmark and sector. Define event windows, entry delay, exits, and overlap treatment in advance. Include delisted names and failed reactions; test subgroups and regime dependence. Report gross and net results with confidence intervals and selection-bias caveats.

## Expected output

Event-study specification, event ledger, abnormal-return summary, cohort breakdowns, and data/identification limitations.

## Guardrails

Do not claim a causal effect from event correlation. Consensus data can be revised or survivorship-biased; record source vintage and availability time.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- https://doi.org/10.3905/jpm.2014.40.5.094

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
