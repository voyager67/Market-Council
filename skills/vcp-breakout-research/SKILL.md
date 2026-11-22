---
name: vcp-breakout-research
description: "Assess volatility contraction structures, supply reduction hypotheses, pivot quality, and breakout confirmation with reproducible criteria."
domain: technical screening
asset_classes: "equities, ETFs"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Volatility Contraction and Breakout Research

## Purpose

Assess volatility contraction structures, supply reduction hypotheses, pivot quality, and breakout confirmation with reproducible criteria.

## Required inputs

Adjusted daily OHLCV; float and liquidity data if available; benchmark-relative returns; sector context; declared contraction and pivot rules.

## Procedure

Validate data continuity, splits, volume units, and minimum liquidity. Identify successive price contractions using a declared swing or volatility method. Compare contraction depth, duration, range overlap, and volume behaviour. Define the pivot mechanically and measure distance from price. Evaluate benchmark and sector context plus gap risk. Classify as candidate, confirmed pattern, failed pattern, or insufficient data and record exact thresholds.

## Expected output

Pattern worksheet with contraction table, pivot definition, volume observations, liquidity screen, relative-strength context, and failure conditions.

## Guardrails

Pattern labels are subjective unless rules are explicit. A contraction does not prove accumulation or predict a breakout. No price target without a separate valuation or scenario model.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://github.com/microsoft/qlib
- https://docs.freqtrade.io/en/latest/backtesting/

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
