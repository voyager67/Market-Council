---
name: sector-theme-rotation
description: "Identify changes in cross-sector and thematic leadership while controlling for universe, lookback, benchmark, and concentration effects."
domain: cross-sectional research
asset_classes: "equities, ETFs"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Sector, Industry and Theme Rotation

## Purpose

Identify changes in cross-sector and thematic leadership while controlling for universe, lookback, benchmark, and concentration effects.

## Required inputs

Point-in-time sector/industry mapping; ETF/constituent total-return series; benchmark; holdings/concentration; calendar alignment.

## Procedure

Declare taxonomy and instrument proxies. Align total returns, currencies, calendars, and corporate actions. Compute relative performance across predeclared horizons. Measure breadth and concentration within each group. Compare leader persistence, dispersion, volatility, and turnover. Distinguish observed rotation from a causal macro explanation.

## Expected output

Rotation matrix with definitions, ranked relative returns, participation, concentration, persistence, and alternative explanations.

## Guardrails

ETF proxies may not represent pure sector exposure. Do not use current index membership for historical results without point-in-time constituents.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://github.com/microsoft/qlib
- https://fred.stlouisfed.org/docs/api/fred/

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
