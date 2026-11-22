---
name: pair-trading-cointegration
description: "Evaluate candidate pairs for economic rationale, stationarity, cointegration, regime stability, and executable spread economics."
domain: relative-value research
asset_classes: "equities, ETFs, futures, crypto"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Statistical Pair Trading Research

## Purpose

Evaluate candidate pairs for economic rationale, stationarity, cointegration, regime stability, and executable spread economics.

## Required inputs

Synchronized adjusted price series; instrument mapping; corporate actions; borrow/funding; transaction costs; formation and test windows.

## Procedure

Establish an economic relationship before statistical testing. Synchronize observations and screen for missingness and non-overlapping sessions. Split formation, validation, and out-of-sample periods. Estimate hedge relationships and test residual/spread properties with stated assumptions. Evaluate parameter stability, structural breaks, costs, borrow, and capacity. Define entry/exit logic only after validation, and preserve failed pairs in the study.

## Expected output

Pair research dossier with rationale, sample definitions, hedge method, diagnostics, costs, stability, and out-of-sample outcomes.

## Guardrails

Correlation alone is not cointegration. Avoid repeatedly searching pairs on the final test period. Do not ignore borrow availability or asynchronous trading.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://github.com/microsoft/qlib
- https://www.quantconnect.com/docs/v2/lean-engine/getting-started

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
