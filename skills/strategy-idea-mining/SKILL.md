---
name: strategy-idea-mining
description: "Convert a market observation into a falsifiable trading hypothesis with measurable features, controls, and a test plan."
domain: systematic research
asset_classes: "multi-asset"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Strategy Idea Mining and Hypothesis Design

## Purpose

Convert a market observation into a falsifiable trading hypothesis with measurable features, controls, and a test plan.

## Required inputs

Observed anomaly or market narrative; asset universe; candidate data sources; plausible mechanism; holding horizon; baseline strategy.

## Procedure

State the observed phenomenon without asserting an edge. Propose a plausible mechanism and alternative explanations. Define target, features, universe, timestamp availability, and holding period. Specify null hypothesis, benchmark, controls, and evaluation metrics. Define sample splits and minimum sample criteria before testing. Record expected failure modes and a stop condition for research.

## Expected output

Research ticket with hypothesis, mechanism, data contract, baseline, test design, evaluation criteria, and kill criteria.

## Guardrails

Do not use LLM-generated hypotheses as empirical findings. Keep ideation separate from validation and never claim an edge before a reproducible test.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://github.com/microsoft/qlib
- https://finrl.ai/

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
