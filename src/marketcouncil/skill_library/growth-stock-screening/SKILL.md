---
name: growth-stock-screening
description: "Screen growth companies using transparent sales, earnings, quality, liquidity, and relative-strength criteria with point-in-time data controls."
domain: equity screening
asset_classes: "equities"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Growth Equity Screening

## Purpose

Screen growth companies using transparent sales, earnings, quality, liquidity, and relative-strength criteria with point-in-time data controls.

## Required inputs

Issuer financials with fiscal periods; share count; earnings history; adjusted price/volume history; sector classification; universe and liquidity rules.

## Procedure

Define universe, accounting currency, fiscal period alignment, and screen thresholds. Verify revenue and earnings periods and distinguish reported from adjusted metrics. Check growth rates, margin direction, cash conversion, leverage, dilution, and capital intensity. Add price/volume and benchmark-relative filters as separate layers. Review sector-specific accounting and cyclical effects. Return raw metric values, exclusions, and missing fields for every candidate.

## Expected output

Ranked candidate table with metric definitions, raw values, data dates, screening exclusions, and manual diligence questions.

## Guardrails

A screen is a retrieval and filtering step, not an investment recommendation. Do not splice fiscal periods or substitute estimated figures without labeling them.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- https://github.com/microsoft/qlib

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
