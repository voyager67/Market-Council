---
name: catalyst-verification
description: "Verify company and market catalysts against timestamped primary sources before incorporating them into a thesis."
domain: event research
version: 1
asset_classes: "equities, commodities, crypto"
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Catalyst Verification

## Purpose

Verify company and market catalysts against timestamped primary sources before incorporating them into a thesis.

## Required inputs

filings, exchange announcements, issuer releases, official transcripts, event time and timezone

## Procedure

Identify the original source. Confirm issuer, instrument, event date, publication date, and whether the information is new. Separate confirmed facts, management claims, and commentary. Record contradictions.

## Expected output

Catalyst ledger with claim, source, timestamp, verification status, materiality hypotheses, and unknowns.

## Guardrails

News summaries are not primary proof. Do not fabricate a URL, quote, filing, or event outcome.

## Evidence standard

Label every statement as an observed input, deterministic calculation, source-backed claim, interpretation, or unresolved assumption. Include source timestamp and scope whenever available. If the required evidence is missing, return an explicit abstention and list the missing inputs instead of filling the gap with inference.

## Research references

- https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- https://www.sec.gov/data-research/sec-data-resources

These are further-reading sources, not endorsements or evidence of strategy profitability. This playbook is independently authored and does not reproduce third-party source text or code.
