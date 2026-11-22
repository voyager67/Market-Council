---
name: signal-postmortem-review
description: "Review closed signals and trades by outcome, market context, execution quality, and rule adherence without equating profit with process quality."
domain: performance review
asset_classes: "multi-asset"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Signal and Trade Postmortem

## Purpose

Review closed signals and trades by outcome, market context, execution quality, and rule adherence without equating profit with process quality.

## Required inputs

Pre-trade record; signal timestamp; entry/exit fills; costs; benchmark; context; rule checklist; comparable trade cohort.

## Procedure

Freeze the original plan and intended signal time. Reconstruct only data that would have been available at the decision time. Separate market outcome, implementation shortfall, and rule compliance. Classify outcome and deviations using stable tags. Compare with a predefined cohort and disclose sample size. Propose one testable process adjustment and a measurement window.

## Expected output

Postmortem with plan-versus-actual timeline, attribution, process scorecard, cohort context, and falsifiable improvement tests.

## Guardrails

Do not declare skill from a tiny sample. Avoid outcome bias and do not automatically increase risk after profitable periods.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://www.freqtrade.io/en/latest/lookahead-analysis/
- https://doi.org/10.3905/jpm.2014.40.5.094

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
