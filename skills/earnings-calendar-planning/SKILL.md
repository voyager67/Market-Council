---
name: earnings-calendar-planning
description: "Build an earnings event calendar with verified timing, source provenance, and explicit pre/post-event exposure questions."
domain: event research
asset_classes: "equities, options"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Earnings Calendar and Event Planning

## Purpose

Build an earnings event calendar with verified timing, source provenance, and explicit pre/post-event exposure questions.

## Required inputs

Issuer or exchange event notice; reporting period; published event time; timezone; instrument positions; option expiry and liquidity data when relevant.

## Procedure

Locate the issuer or exchange primary notice and record publication time. Distinguish confirmed date/time from vendor estimates. Normalize timezone and label before-open, after-close, or unknown. Map held and watchlist instruments and related options expiries. Identify gaps, borrow, liquidity, and overnight exposure. Set a refresh timestamp and human review checklist.

## Expected output

Earnings calendar with verified or estimated status, primary-source links, event timezone, affected positions, and pre/post-event review gates.

## Guardrails

Never infer an event time from a generic calendar badge. Event calendars change; require a current source and explicit last-checked timestamp.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- https://www.optionseducation.org/theoptionseducationcenter/learning-resources-by-topic/greeks-and-volatility

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
