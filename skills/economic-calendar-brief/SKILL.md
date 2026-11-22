---
name: economic-calendar-brief
description: "Turn official economic release schedules into timestamped event-risk briefs with scenario channels and data-vintage awareness."
domain: macro event research
asset_classes: "equities, fixed income, FX, commodities, futures"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Economic Calendar Briefing

## Purpose

Turn official economic release schedules into timestamped event-risk briefs with scenario channels and data-vintage awareness.

## Required inputs

Official statistical agency or central-bank calendar; release time and timezone; consensus source and vintage; relevant time series; portfolio exposures.

## Procedure

Prefer the issuing statistical agency or central bank for schedule and release documents. Verify event status, timezone, units, seasonal adjustment, and revision policy. Distinguish first release from subsequent revisions and benchmark definitions. Map direct and indirect channels to instruments and sectors. Prepare scenario branches without assigning unsupported probabilities. Expire the brief after the event or when the schedule changes.

## Expected output

Event brief with source hierarchy, publication timestamp, verified actual/consensus/prior fields, possible transmission channels, and recheck requirements.

## Guardrails

Do not substitute a news aggregator clock for the official release schedule. Avoid presenting estimates as official data.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://fred.stlouisfed.org/docs/api/fred/
- https://www.sec.gov/about/developer-resources

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
