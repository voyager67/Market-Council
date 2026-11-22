---
name: futures-roll-and-term-structure
description: "Examine futures curve shape, roll yield, contract transitions, and continuous-series construction without conflating synthetic prices with tradable contracts."
domain: derivatives market structure
asset_classes: "futures, commodities, rates, equity indices"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Futures Roll and Term-Structure Research

## Purpose

Examine futures curve shape, roll yield, contract transitions, and continuous-series construction without conflating synthetic prices with tradable contracts.

## Required inputs

Exchange contract specs; dated contract prices; expiry calendar; volume/open interest; roll rule; currency; collateral assumptions.

## Procedure

Identify contract month codes, expiry, first notice, and last trade dates. Construct the curve from simultaneously timestamped contracts. Define roll timing and weight rules before building a continuous series. Separate calendar spread and term structure from spot-price movement. Quantify roll methodology sensitivity and liquidity migration. Evaluate roll costs and basis risk in any strategy interpretation.

## Expected output

Curve and roll report with contract map, curve measures, roll schedule, synthetic-series method, cost assumptions, and caveats.

## Guardrails

A back-adjusted continuous series is not a directly tradable price. Do not ignore delivery, notice, or expiry obligations.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://nautilustrader.io/docs/latest/concepts/overview/
- https://www.quantconnect.com/docs/v2/lean-engine/getting-started

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
