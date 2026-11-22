---
name: technical-structure
description: "Describe price structure, trend, momentum, support/resistance hypotheses, and volatility using clearly stated timeframes."
domain: technical research
version: 1
asset_classes: "multi-asset"
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Technical Structure

## Purpose

Describe price structure, trend, momentum, support/resistance hypotheses, and volatility using clearly stated timeframes.

## Required inputs

timestamped OHLCV bars; timeframe; corporate-action adjustment status; benchmark if relative analysis is requested

## Procedure

Validate continuity and units. State the timeframe and lookback. Describe observed swings and trend context. Distinguish computed metrics from chart interpretation. Present levels as hypotheses with invalidation conditions.

## Expected output

Technical structure note with timeframe, observations, levels, caveats, and invalidation conditions.

## Guardrails

Do not promise predictive power. Do not invent candles or assume adjusted data. Avoid unsupported precision in levels.

## Evidence standard

Label every statement as an observed input, deterministic calculation, source-backed claim, interpretation, or unresolved assumption. Include source timestamp and scope whenever available. If the required evidence is missing, return an explicit abstention and list the missing inputs instead of filling the gap with inference.

## Research references

- https://github.com/microsoft/qlib
- https://docs.freqtrade.io/en/latest/backtesting/

These are further-reading sources, not endorsements or evidence of strategy profitability. This playbook is independently authored and does not reproduce third-party source text or code.
