---
name: market-regime
description: "Classify the prevailing regime from supplied price, volatility, breadth, and macro evidence without treating a label as a forecast."
domain: market research
version: 1
asset_classes: "multi-asset"
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Market Regime

## Purpose

Classify the prevailing regime from supplied price, volatility, breadth, and macro evidence without treating a label as a forecast.

## Required inputs

price history; benchmark and breadth series; realised volatility; macro context when relevant

## Procedure

Separate trend, volatility, breadth, and macro observations. Identify the regime only when independent dimensions are available. State conflicting evidence and the timeframe. Define what evidence would change the classification.

## Expected output

Regime label with confidence rationale, supporting observations, conflicts, missing inputs, and reassessment triggers.

## Guardrails

Never infer macro conditions from price alone. Do not convert regime labels into automatic exposure recommendations.

## Evidence standard

Label every statement as an observed input, deterministic calculation, source-backed claim, interpretation, or unresolved assumption. Include source timestamp and scope whenever available. If the required evidence is missing, return an explicit abstention and list the missing inputs instead of filling the gap with inference.

## Research references

- https://fred.stlouisfed.org/docs/api/fred/
- https://github.com/microsoft/qlib

These are further-reading sources, not endorsements or evidence of strategy profitability. This playbook is independently authored and does not reproduce third-party source text or code.
