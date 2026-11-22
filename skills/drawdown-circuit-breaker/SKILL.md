---
name: drawdown-circuit-breaker
description: "Apply trader-defined drawdown thresholds and portfolio risk limits as deterministic stop-and-review gates."
domain: risk controls
asset_classes: "multi-asset"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Drawdown and Risk Circuit Breaker

## Purpose

Apply trader-defined drawdown thresholds and portfolio risk limits as deterministic stop-and-review gates.

## Required inputs

Equity curve; peak definition; realized/unrealized PnL; open risk; trader-defined daily/weekly/total thresholds; account timezone.

## Procedure

Validate equity timestamps and whether deposits/withdrawals are neutralized. Calculate peak-to-trough and period drawdown consistently. Compare values with explicit user-approved thresholds. Include open positions, correlated exposures, and gap scenarios when supplied. Return NORMAL, REVIEW, or HALT according to configured policy. Record reset conditions and require named human approval before re-enabling risk.

## Expected output

Circuit-breaker status, metric calculations, threshold comparison, affected risk capacity, audit inputs, and human restart checklist.

## Guardrails

Never invent drawdown tolerances. A circuit-breaker result is a policy control, not a prediction. The software does not close positions or block broker orders.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://finrl.ai/
- https://nautilustrader.io/docs/latest/concepts/live/

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
