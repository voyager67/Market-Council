---
name: trade-plan-discipline
description: "Check whether a proposed plan is complete, internally consistent, and compatible with explicit trader-defined limits."
domain: pre-trade controls
version: 1
asset_classes: "multi-asset"
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Trade Plan Discipline

## Purpose

Check whether a proposed plan is complete, internally consistent, and compatible with explicit trader-defined limits.

## Required inputs

thesis; entry trigger; invalidation; stop; size; max risk; horizon; liquidity; event context; portfolio exposure

## Procedure

Check required fields. Validate stop direction and arithmetic. Compare proposed risk against user-supplied limits. List unresolved assumptions and require explicit human acknowledgement.

## Expected output

Pre-trade checklist result: complete/incomplete, arithmetic checks, conflicts, and human sign-off requirements.

## Guardrails

Never invent the trader’s risk appetite. A completed checklist is not a recommendation or order approval.

## Evidence standard

Label every statement as an observed input, deterministic calculation, source-backed claim, interpretation, or unresolved assumption. Include source timestamp and scope whenever available. If the required evidence is missing, return an explicit abstention and list the missing inputs instead of filling the gap with inference.

## Research references

- https://nautilustrader.io/docs/latest/concepts/live/
- https://www.quantconnect.com/docs/v2/lean-engine/getting-started

These are further-reading sources, not endorsements or evidence of strategy profitability. This playbook is independently authored and does not reproduce third-party source text or code.
