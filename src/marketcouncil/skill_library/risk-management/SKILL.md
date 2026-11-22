---
name: risk-management
description: "Translate a proposed trade plan into explicit loss scenarios, risk budget, and operational checks."
domain: trade risk
version: 1
asset_classes: "multi-asset"
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Risk Management

## Purpose

Translate a proposed trade plan into explicit loss scenarios, risk budget, and operational checks.

## Required inputs

equity/net liquidation value; entry; stop; side; instrument multiplier; fees; slippage; liquidity; portfolio context

## Procedure

Validate side/stop relationship and contract units. Calculate risk per unit and position cap deterministically. Stress gaps and slippage. Identify portfolio-level interactions. Record assumptions for every estimate.

## Expected output

Risk worksheet with budget, units, notional, scenario loss, assumptions, and unresolved controls.

## Guardrails

Model outputs must not set risk limits. Stop-loss estimates are not guaranteed maximum losses; gaps and execution can exceed them.

## Evidence standard

Label every statement as an observed input, deterministic calculation, source-backed claim, interpretation, or unresolved assumption. Include source timestamp and scope whenever available. If the required evidence is missing, return an explicit abstention and list the missing inputs instead of filling the gap with inference.

## Research references

- https://nautilustrader.io/docs/latest/concepts/live/
- https://finrl.ai/

These are further-reading sources, not endorsements or evidence of strategy profitability. This playbook is independently authored and does not reproduce third-party source text or code.
