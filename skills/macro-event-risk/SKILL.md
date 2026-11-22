---
name: macro-event-risk
description: "Map macroeconomic releases, policy events, and cross-asset sensitivities into scenario risks."
domain: macro research
version: 1
asset_classes: "equities, fixed income, FX, commodities"
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Macro Event Risk

## Purpose

Map macroeconomic releases, policy events, and cross-asset sensitivities into scenario risks.

## Required inputs

official release calendar; source timestamps; instrument exposures; relevant rates, FX, inflation and growth series

## Procedure

Prefer official sources. Verify release time and timezone. Distinguish scheduled events from speculation. Map exposure channels and plausible scenarios. State what is unknown and when the view expires.

## Expected output

Event-risk map with calendar, affected exposures, scenarios, source metadata, and monitoring triggers.

## Guardrails

Do not invent calendar entries or current values. Never imply a macro event has a deterministic market outcome.

## Evidence standard

Label every statement as an observed input, deterministic calculation, source-backed claim, interpretation, or unresolved assumption. Include source timestamp and scope whenever available. If the required evidence is missing, return an explicit abstention and list the missing inputs instead of filling the gap with inference.

## Research references

- https://fred.stlouisfed.org/docs/api/fred/
- https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm

These are further-reading sources, not endorsements or evidence of strategy profitability. This playbook is independently authored and does not reproduce third-party source text or code.
