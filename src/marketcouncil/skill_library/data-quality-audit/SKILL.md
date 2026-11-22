---
name: data-quality-audit
description: "Audit market and fundamental datasets for schema validity, temporal integrity, symbol mapping, stale observations, and source provenance."
domain: data engineering
asset_classes: "multi-asset"
version: 1
source_basis: "Independently authored methodology synthesis; see cited public research and official documentation."
---

# Market Data Quality and Provenance Audit

## Purpose

Audit market and fundamental datasets for schema validity, temporal integrity, symbol mapping, stale observations, and source provenance.

## Required inputs

Raw files or provider payloads; schema; instrument master; timestamp conventions; source metadata; adjustment policy; data dictionary.

## Procedure

Preserve immutable raw input and compute a content hash. Validate schema, types, units, uniqueness, and null patterns. Check timestamp timezone, ordering, session gaps, revision and availability dates. Reconcile symbols, venues, currencies, contract rolls, and corporate actions. Flag stale, zero, implausible, and discontinuous values with explicit rules. Emit a machine-readable quality report and never silently repair raw data.

## Expected output

Data quality report with file hash, schema result, defect counts, affected rows, lineage fields, and remediation recommendations.

## Guardrails

Do not overwrite raw source records. Do not interpret missing values as zero. Every transformation must be reproducible and documented.

## Evidence standard

For each conclusion, distinguish: (1) supplied observation, (2) deterministic calculation, (3) primary-source fact, (4) interpretation, and (5) unresolved assumption. Preserve source URI, publisher, publication time, observation time, timezone, instrument/venue scope, and data vintage where relevant. If a necessary field is unavailable, mark the result incomplete or abstain; do not infer it from narrative context.

## Research references

- https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- https://github.com/ccxt/ccxt

These references are further reading, not endorsements or evidence that this skill or any strategy is profitable. This playbook is independently authored and does not reproduce third-party source text or code.
