---
name: sector-relative-strength
description: "Compare sector and instrument performance against a defined benchmark and consistent universe."
domain: cross-sectional research
version: 1
asset_classes: "equities, ETFs"
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Sector Relative Strength

## Purpose

Compare sector and instrument performance against a defined benchmark and consistent universe.

## Required inputs

sector/index constituents; benchmark series; adjusted prices; currency; lookback and rebalance rules

## Procedure

Confirm constituent history and benchmark. Align calendars and currencies. Compute relative returns over declared windows. Check concentration and survivorship. Identify breadth behind aggregate results.

## Expected output

Relative-strength table with benchmark, windows, dispersion, concentration, and caveats.

## Guardrails

Do not compare unmatched dates or currencies. Relative strength is descriptive, not a stand-alone buy signal.

## Evidence standard

Label every statement as an observed input, deterministic calculation, source-backed claim, interpretation, or unresolved assumption. Include source timestamp and scope whenever available. If the required evidence is missing, return an explicit abstention and list the missing inputs instead of filling the gap with inference.

## Research references

- https://github.com/microsoft/qlib
- https://fred.stlouisfed.org/docs/api/fred/

These are further-reading sources, not endorsements or evidence of strategy profitability. This playbook is independently authored and does not reproduce third-party source text or code.
