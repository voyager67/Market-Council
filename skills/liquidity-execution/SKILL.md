---
name: liquidity-execution
description: "Evaluate execution feasibility from supplied volume, spread, depth, venue, and order constraints."
domain: market microstructure
version: 1
asset_classes: "multi-asset"
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Liquidity and Execution

## Purpose

Evaluate execution feasibility from supplied volume, spread, depth, venue, and order constraints.

## Required inputs

venue and instrument; timestamped spreads/depth; volume; order size; trading session; fee schedule

## Procedure

Check feed freshness and venue coverage. Estimate participation rate only with comparable volume windows. Assess spread, depth, volatility, and market impact assumptions. Describe execution alternatives without placing orders.

## Expected output

Liquidity assessment with data timestamps, participation assumptions, venue limitations, and execution risks.

## Guardrails

Never fabricate order-book depth. No order routing or broker execution is provided.

## Evidence standard

Label every statement as an observed input, deterministic calculation, source-backed claim, interpretation, or unresolved assumption. Include source timestamp and scope whenever available. If the required evidence is missing, return an explicit abstention and list the missing inputs instead of filling the gap with inference.

## Research references

- https://nautilustrader.io/docs/latest/concepts/overview/
- https://github.com/ccxt/ccxt

These are further-reading sources, not endorsements or evidence of strategy profitability. This playbook is independently authored and does not reproduce third-party source text or code.
