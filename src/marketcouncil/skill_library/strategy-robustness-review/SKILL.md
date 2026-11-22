---
name: strategy-robustness-review
description: "Challenge strategy results for data leakage, selection bias, unstable parameters, execution realism, and regime dependence."
domain: systematic validation
asset_classes: "multi-asset"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Strategy Robustness and Overfitting Review

## Purpose

Challenge strategy results for data leakage, selection bias, unstable parameters, execution realism, and regime dependence.

## Required inputs

Strategy specification; raw and point-in-time datasets; search logs; train/validation/test periods; benchmark; fee/slippage/borrow assumptions.

## Procedure

Reconstruct research chronology and data availability. Audit survivorship, corporate actions, revisions, leakage, and label construction. Review parameter-search multiplicity and holdout contamination. Stress costs, delays, spread, fill assumptions, and market capacity. Run walk-forward, subperiod, universe, and parameter stability checks. Report every failed test and whether the test set remains untouched.

## Expected output

Robustness review with severity-ranked threats, affected metrics, reproducibility requirements, and pass/conditional/fail assessment.

## Guardrails

Never hide a failed test or select a better metric after seeing results without disclosure. A backtest pass does not establish future performance.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://www.freqtrade.io/en/latest/lookahead-analysis/
- https://docs.freqtrade.io/en/latest/backtesting/
- https://doi.org/10.3905/jpm.2014.40.5.094

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
