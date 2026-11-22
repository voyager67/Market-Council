---
name: portfolio-exposure
description: "Review concentration, factor, sector, currency, liquidity, and correlated exposure using explicit portfolio inputs."
domain: portfolio risk
version: 1
asset_classes: "multi-asset"
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Portfolio Exposure

## Purpose

Review concentration, factor, sector, currency, liquidity, and correlated exposure using explicit portfolio inputs.

## Required inputs

holdings with quantities and prices; instrument metadata; cash; benchmark; currency; account scope

## Procedure

Reconcile market values and cash. Classify exposures and identify missing mappings. Aggregate concentration and correlated risk cautiously. Distinguish gross, net, and derivative notional.

## Expected output

Exposure report with reconciliations, top concentrations, factor gaps, and review questions.

## Guardrails

Do not infer holdings from a watchlist. Do not treat derivative notional as equivalent to cash exposure without contract details.

## Evidence standard

Label every statement as an observed input, deterministic calculation, source-backed claim, interpretation, or unresolved assumption. Include source timestamp and scope whenever available. If the required evidence is missing, return an explicit abstention and list the missing inputs instead of filling the gap with inference.

## Research references

- https://nautilustrader.io/docs/latest/concepts/overview/
- https://finrl.ai/

These are further-reading sources, not endorsements or evidence of strategy profitability. This playbook is independently authored and does not reproduce third-party source text or code.
