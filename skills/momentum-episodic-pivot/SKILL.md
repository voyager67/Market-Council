---
name: momentum-episodic-pivot
description: "Evaluate abrupt repricing events and sustained momentum using event timing, liquidity, relative strength, and post-event behaviour."
domain: momentum strategies
asset_classes: "equities"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Momentum and Episodic Pivot Research

## Purpose

Evaluate abrupt repricing events and sustained momentum using event timing, liquidity, relative strength, and post-event behaviour.

## Required inputs

Timestamped catalyst and filing data; adjusted intraday/daily bars; volume; float; benchmark; spread/liquidity; event-time timezone.

## Procedure

Identify the event timestamp and whether it was known before the price move. Measure gap, intraday range, volume expansion, and post-event drift over predeclared windows. Compare reactions with sector and benchmark moves. Separate new information from scheduled or anticipated events. Model entry delay, spread, gap, and halt risk. Preserve all event candidates, including failures, for unbiased cohort analysis.

## Expected output

Event cohort record with catalyst quality, reaction metrics, comparison groups, liquidity, subsequent path, and uncertainty.

## Guardrails

Do not treat a large gap or volume burst as proof of durable information advantage. Avoid hindsight event selection and survivorship filtering.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- https://docs.freqtrade.io/en/latest/backtesting/

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
