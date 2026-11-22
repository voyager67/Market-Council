---
name: market-maker-microstructure
description: "Interpret order-book and trade-flow snapshots with venue, sequence, depth, and latency constraints explicitly represented."
domain: market microstructure
asset_classes: "equities, futures, crypto"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Order Book and Market Microstructure Review

## Purpose

Interpret order-book and trade-flow snapshots with venue, sequence, depth, and latency constraints explicitly represented.

## Required inputs

Venue; instrument; L2/L3 snapshot or stream; sequence identifiers; timestamp/latency; trade prints; tick size; lot size.

## Procedure

Validate venue and instrument identifiers, tick/lot sizes, sequence continuity, and snapshot freshness. Compute spread, depth by distance, imbalance, and trade aggressor proxies when fields permit. Compare multiple snapshot windows to avoid treating one frame as persistent liquidity. Flag crossed/locked markets and outlier quotes. Discuss queue, cancellation, and market-impact limitations based on data granularity. Separate venue-specific observations from consolidated-market conclusions.

## Expected output

Microstructure memo with data freshness, spread/depth metrics, imbalance method, sequence checks, and execution caveats.

## Guardrails

A displayed book is not guaranteed executable liquidity. Do not infer spoofing or intent from isolated cancellations.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://github.com/ccxt/ccxt
- https://github.com/binance/binance-spot-api-docs

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
