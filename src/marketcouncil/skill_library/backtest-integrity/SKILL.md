---
name: backtest-integrity
description: "Audit a backtest for look-ahead, survivorship, leakage, overfitting, unrealistic fills, and hidden costs."
domain: strategy validation
version: 1
asset_classes: "multi-asset"
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Backtest Integrity

## Purpose

Audit a backtest for look-ahead, survivorship, leakage, overfitting, unrealistic fills, and hidden costs.

## Required inputs

strategy source; raw data provenance; event timestamps; universe history; execution model; fees and slippage

## Procedure

Trace features to availability timestamps. Review universe membership and delisted assets. Check next-bar/fill conventions and corporate actions. Audit parameter search and holdout reuse. Compare gross/net performance and stress costs.

## Expected output

Backtest audit with issue severity, evidence, affected results, remediation, and rerun criteria.

## Guardrails

A backtest is not evidence of future profitability. Do not endorse results when data lineage or execution assumptions are unknown.

## Evidence standard

Label every statement as an observed input, deterministic calculation, source-backed claim, interpretation, or unresolved assumption. Include source timestamp and scope whenever available. If the required evidence is missing, return an explicit abstention and list the missing inputs instead of filling the gap with inference.

## Research references

- https://www.freqtrade.io/en/latest/lookahead-analysis/
- https://doi.org/10.3905/jpm.2014.40.5.094

These are further-reading sources, not endorsements or evidence of strategy profitability. This playbook is independently authored and does not reproduce third-party source text or code.
