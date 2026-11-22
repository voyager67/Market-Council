---
name: market-breadth
description: "Evaluate participation and breadth from constituent-level advances, declines, new highs/lows, and participation series."
domain: market internals
version: 1
asset_classes: "equities, ETFs"
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Market Breadth

## Purpose

Evaluate participation and breadth from constituent-level advances, declines, new highs/lows, and participation series.

## Required inputs

constituent universe; timestamped advances/declines; new highs/lows; index membership rules

## Procedure

Check universe definition and survivorship issues. Align dates and sessions. Compute participation ratios only from matched observations. Compare breadth with index direction and identify divergences.

## Expected output

Breadth dashboard table with universe, dates, measures, divergences, and data-quality notes.

## Guardrails

No breadth conclusion from a single index price series. Flag stale or incomplete constituent data.

## Evidence standard

Label every statement as an observed input, deterministic calculation, source-backed claim, interpretation, or unresolved assumption. Include source timestamp and scope whenever available. If the required evidence is missing, return an explicit abstention and list the missing inputs instead of filling the gap with inference.

## Research references

- https://github.com/microsoft/qlib
- https://docs.freqtrade.io/en/latest/backtesting/

These are further-reading sources, not endorsements or evidence of strategy profitability. This playbook is independently authored and does not reproduce third-party source text or code.
