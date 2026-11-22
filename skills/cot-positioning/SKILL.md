---
name: cot-positioning
description: "Interpret CFTC Commitments of Traders data with correct report type, participant category, open-interest denominator, and reporting lag."
domain: futures positioning
asset_classes: "futures, commodities, FX"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Commitments of Traders Positioning Analysis

## Purpose

Interpret CFTC Commitments of Traders data with correct report type, participant category, open-interest denominator, and reporting lag.

## Required inputs

CFTC report type; market code; report date; participant categories; long/short/spread positions; open interest; contract mapping.

## Procedure

Select the correct futures-only or futures-and-options report and market. Use the report stated Tuesday positioning date, not publication date, as observation date. Reconcile participant buckets and open interest. Compute net and concentration measures with explicit denominators. Compare history using consistent classifications and contract continuity. Describe positioning extremes as context; test any contrarian hypothesis separately.

## Expected output

Positioning report with report vintage, market identity, participant definitions, net-position series, normalization, and caveats.

## Guardrails

COT is a periodic snapshot, not real-time flow. Do not treat participant labels as intent or directional certainty.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
