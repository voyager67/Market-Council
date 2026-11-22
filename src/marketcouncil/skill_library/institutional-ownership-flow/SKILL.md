---
name: institutional-ownership-flow
description: "Assess reported institutional ownership and flow proxies while respecting filing lags, disclosure thresholds, and the difference between holdings and current trading."
domain: ownership and flow research
asset_classes: "equities, ETFs"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Institutional Ownership and Flow Research

## Purpose

Assess reported institutional ownership and flow proxies while respecting filing lags, disclosure thresholds, and the difference between holdings and current trading.

## Required inputs

13F filings and filing dates; issuer CIK/ticker mapping; security identifiers; shares/value; fund identifiers; price/float; corporate actions.

## Procedure

Retrieve primary filings and record period end, filing date, amendment status, and manager identity. Normalize security identifiers and corporate-action changes. Separate new, increased, reduced, and exited reported positions. Scale ownership to appropriate shares outstanding and note denominator timing. Check whether filings are incomplete, confidentially omitted, or amended. State clearly that reported holdings are lagged snapshots, not intraday flow.

## Expected output

Institutional-ownership change table with filer, period, filing date, identifiers, estimated share change, source links, and lag limitations.

## Guardrails

Do not call 13F filings real-time institutional flow. Do not infer current position, hedge, or intent from a stale report.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- https://www.sec.gov/data-research/sec-data-resources

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
