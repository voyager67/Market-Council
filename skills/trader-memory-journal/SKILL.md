---
name: trader-memory-journal
description: "Maintain a structured, timestamped record of hypotheses, decisions, planned risk, deviations, and thesis lifecycle changes."
domain: trader process
asset_classes: "multi-asset"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Trader Memory and Thesis Journal

## Purpose

Maintain a structured, timestamped record of hypotheses, decisions, planned risk, deviations, and thesis lifecycle changes.

## Required inputs

Trader-authored thesis; instrument; timestamp; source links; entry/exit plan; risk assumptions; decision outcome; post-trade notes.

## Procedure

Create an immutable decision record before the trade or research decision. Separate observation, hypothesis, planned action, and actual action. Link source IDs and preserve source as-of time. Record edits as new versions rather than silently overwriting the original rationale. Link related trades to a thesis lifecycle. Schedule post-event and post-close reviews with outcome and process fields kept separate.

## Expected output

Journal entry schema with thesis ID, version, source ledger, plan, actual actions, deviations, review date, and unresolved lessons.

## Guardrails

Do not infer a trader's psychology or personal characteristics. Avoid retrospective edits that make the original thesis appear more accurate than it was.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://github.com/microsoft/qlib
- https://arxiv.org/abs/2412.20138

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
