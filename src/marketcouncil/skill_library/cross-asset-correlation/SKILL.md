---
name: cross-asset-correlation
description: "Assess dependence across assets using aligned returns, regime splits, tail co-movement, and concentration rather than relying on one correlation matrix."
domain: cross-asset risk
asset_classes: "equities, rates, FX, commodities, crypto"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Cross-Asset Dependence and Stress Review

## Purpose

Assess dependence across assets using aligned returns, regime splits, tail co-movement, and concentration rather than relying on one correlation matrix.

## Required inputs

Synchronized total-return series; currency and unit metadata; instrument calendar; declared windows; holdings/exposures; stress scenarios.

## Procedure

Align return timestamps and quote currencies. Separate local-currency and base-currency returns when conversion matters. Calculate pairwise and rolling dependence using declared estimators. Compare normal periods with stress episodes and downside-tail co-movement. Identify concentration through common factors and liquidity channels. Report estimation uncertainty and sensitivity to windows and missing observations.

## Expected output

Cross-asset dependency report with sample windows, correlations, downside co-movement, factor overlap, and stress limitations.

## Guardrails

Correlation is not causation and can change abruptly. Do not call a portfolio diversified based solely on low historical correlation.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://github.com/microsoft/qlib
- https://nautilustrader.io/docs/latest/concepts/overview/

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
