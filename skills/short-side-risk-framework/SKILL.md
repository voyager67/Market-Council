---
name: short-side-risk-framework
description: "Review borrow, squeeze, gap, financing, recall, margin, and asymmetrical loss risks in a proposed short thesis."
domain: short-selling risk
asset_classes: "equities, ETFs, futures, crypto"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Short-Side Trade Risk Framework

## Purpose

Review borrow, squeeze, gap, financing, recall, margin, and asymmetrical loss risks in a proposed short thesis.

## Required inputs

Instrument and venue; borrow availability/rate; locate/recall terms; margin model; liquidity; entry/stop; corporate actions; risk limits.

## Procedure

Confirm whether instrument can be shorted and under what venue rules. Verify borrow/locate evidence and timestamp, including recall and hard-to-borrow risk. Model price gaps, squeezes, borrow costs, dividends owed, and margin changes. Validate stop direction and position risk with contract/lot constraints. Stress liquidity during halts or fast markets. Require separate human approval and contingency plan.

## Expected output

Short-side risk sheet with borrow status, financing, gap/squeeze cases, stop assumptions, margin sensitivity, and no-go conditions.

## Guardrails

Short losses can exceed the initial risk estimate and borrow may be recalled. Do not assume locate availability from a ticker alone.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://www.sec.gov/data-research/sec-data-resources
- https://nautilustrader.io/docs/latest/concepts/live/

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
