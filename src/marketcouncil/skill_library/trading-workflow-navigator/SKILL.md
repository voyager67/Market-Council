---
name: trading-workflow-navigator
description: "Route a trader's stated objective to the correct research skills, specialist agents, evidence requirements, and decision gates."
domain: research operations
asset_classes: "multi-asset"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Trading Workflow Navigator

## Purpose

Route a trader's stated objective to the correct research skills, specialist agents, evidence requirements, and decision gates.

## Required inputs

Trader objective; asset class; holding horizon; jurisdiction/venue; available data; constraints; risk policy.

## Procedure

Parse the objective into instrument, task, horizon, and constraints. Identify required evidence and unavailable inputs. Select a workflow manifest and required skills based on metadata. Distinguish offline/manual pathways from integrations that need external credentials. Identify mandatory human decision gates and handoff artifacts. Report any unshipped capability as unavailable instead of inventing an execution path.

## Expected output

Workflow recommendation with intent classification, skill sequence, agents, input checklist, dependency map, human gates, and honest gaps.

## Guardrails

Routing does not validate a strategy or provide a trading recommendation. Never claim an integration exists unless it is implemented and tested.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://tradingagents-ai.github.io/
- https://docs.openbb.co/

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
