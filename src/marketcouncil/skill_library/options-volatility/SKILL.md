---
name: options-volatility
description: "Interpret option-implied volatility, skew, term structure, and Greeks from a specified contract surface."
domain: derivatives research
version: 1
asset_classes: "options, equities, ETFs"
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Options Volatility

## Purpose

Interpret option-implied volatility, skew, term structure, and Greeks from a specified contract surface.

## Required inputs

option chain; expiry; strike; call/put; underlying price; rates/dividends; contract multiplier; timestamp

## Procedure

Validate contract specifications and quote freshness. Check bid/ask quality and open interest. Separate implied from realised volatility. Explain Greeks and model assumptions. Present payoff and expiry risks.

## Expected output

Options note with contract universe, volatility surface, Greeks assumptions, payoff risks, and data gaps.

## Guardrails

Do not infer a full volatility surface from one quote. No options order instructions; assignment and exercise risk must remain explicit.

## Evidence standard

Label every statement as an observed input, deterministic calculation, source-backed claim, interpretation, or unresolved assumption. Include source timestamp and scope whenever available. If the required evidence is missing, return an explicit abstention and list the missing inputs instead of filling the gap with inference.

## Research references

- https://www.optionseducation.org/theoptionseducationcenter/learning-resources-by-topic/greeks-and-volatility
- https://prd-web.optionseducation.org/advancedconcepts/understanding-options-greeks

These are further-reading sources, not endorsements or evidence of strategy profitability. This playbook is independently authored and does not reproduce third-party source text or code.
