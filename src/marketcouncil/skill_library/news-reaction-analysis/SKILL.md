---
name: news-reaction-analysis
description: "Assess how price and liquidity responded to a timestamped news item without confusing temporal sequence with causation."
domain: news and event research
asset_classes: "equities, FX, commodities, crypto"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# News Reaction and Price-Response Analysis

## Purpose

Assess how price and liquidity responded to a timestamped news item without confusing temporal sequence with causation.

## Required inputs

Original news/filing source; publication and event timestamps; timezone; instrument bars; benchmark; sector/peer series; volume and spread.

## Procedure

Preserve the original source, publication time, update history, and event time. Check whether information was already public or anticipated. Align event time to venue sessions and use the first tradable bar after release. Compare instrument response with benchmark and peers. Inspect spread, volume, volatility, gaps, and subsequent reversals. Classify the reaction as observed association and list alternative drivers.

## Expected output

News reaction note with source chain, timing alignment, event window, abnormal-response context, confounders, and follow-up evidence.

## Guardrails

Do not infer causality from a price move after a headline. Aggregators and reposts are not independent sources.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- https://github.com/binance/binance-spot-api-docs

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
