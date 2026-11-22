---
name: crypto-regime-assessment
description: "Assess crypto market structure across venue liquidity, funding, basis, open interest, volatility, and cross-asset context."
domain: digital asset research
asset_classes: "crypto spot, perpetuals, futures"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Crypto Market Regime Assessment

## Purpose

Assess crypto market structure across venue liquidity, funding, basis, open interest, volatility, and cross-asset context.

## Required inputs

Venue-specific spot/perpetual bars; funding history; open interest; mark/index prices; liquidation methodology; order-book snapshots; timestamps.

## Procedure

Identify each venue, instrument type, contract specification, and quote currency. Reconcile symbol aliases and contract multipliers. Compare spot/perpetual basis, funding, open interest, and liquidation measures with consistent timestamps. Measure venue concentration, depth and spread dispersion. Review 24/7 calendar effects, custody and counterparty risks. Report venue-specific observations before any market-wide interpretation.

## Expected output

Crypto regime brief with venue map, basis/funding state, liquidity and concentration, volatility context, data quality, and stress conditions.

## Guardrails

Do not aggregate exchange volume blindly. Do not compare perpetual funding across different intervals or settlement conventions. Do not assume uninterrupted exchange availability.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://github.com/ccxt/ccxt
- https://github.com/binance/binance-spot-api-docs

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
