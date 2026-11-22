---
name: quantitative-research
description: "Turn a trading idea into a falsifiable research protocol with explicit data, hypothesis, and evaluation metrics."
domain: quant research
version: 1
asset_classes: "multi-asset"
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Quantitative Research

## Purpose

Turn a trading idea into a falsifiable research protocol with explicit data, hypothesis, and evaluation metrics.

## Required inputs

hypothesis; point-in-time dataset; universe; benchmark; horizon; transaction costs; predeclared metrics

## Procedure

Write null and alternative hypotheses. Freeze inclusion rules before evaluation. Check timestamps, labels, missingness, and universe changes. Specify train/validation/test boundaries. Define baselines and uncertainty estimates.

## Expected output

Research protocol with hypothesis, data lineage, controls, metrics, baselines, and decision criteria.

## Guardrails

Do not claim alpha or improvement from in-sample results. Avoid repeated test-set peeking and undisclosed researcher degrees of freedom.

## Evidence standard

Label every statement as an observed input, deterministic calculation, source-backed claim, interpretation, or unresolved assumption. Include source timestamp and scope whenever available. If the required evidence is missing, return an explicit abstention and list the missing inputs instead of filling the gap with inference.

## Research references

- https://github.com/microsoft/qlib
- https://finrl.ai/

These are further-reading sources, not endorsements or evidence of strategy profitability. This playbook is independently authored and does not reproduce third-party source text or code.
