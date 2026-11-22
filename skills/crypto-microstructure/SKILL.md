---
name: crypto-microstructure
description: "Assess digital-asset venue, funding, basis, liquidation, and order-book risks with venue-specific context."
domain: digital asset markets
version: 1
asset_classes: "crypto spot, perpetuals, futures"
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Crypto Microstructure

## Purpose

Assess digital-asset venue, funding, basis, liquidation, and order-book risks with venue-specific context.

## Required inputs

asset and contract; venue; funding and open interest; mark/index prices; depth; liquidation data; timestamp

## Procedure

Identify spot/perpetual/future instrument type. Verify venue and contract specifications. Separate exchange-specific observations from market-wide conclusions. Account for 24/7 sessions and fragmented liquidity.

## Expected output

Crypto microstructure note with venue scope, leverage/funding risk, basis, liquidity, and missing data.

## Guardrails

Do not transfer equity assumptions to crypto. Do not treat exchange-reported volume as universally reliable.

## Evidence standard

Label every statement as an observed input, deterministic calculation, source-backed claim, interpretation, or unresolved assumption. Include source timestamp and scope whenever available. If the required evidence is missing, return an explicit abstention and list the missing inputs instead of filling the gap with inference.

## Research references

- https://github.com/ccxt/ccxt
- https://github.com/binance/binance-spot-api-docs

These are further-reading sources, not endorsements or evidence of strategy profitability. This playbook is independently authored and does not reproduce third-party source text or code.
