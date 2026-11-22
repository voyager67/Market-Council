"""Human-readable and machine-readable research report rendering."""

from __future__ import annotations

import json

from .models import CouncilReport


def render_json(report: CouncilReport) -> str:
    return json.dumps(report.to_dict(), indent=2, ensure_ascii=False)


def render_markdown(report: CouncilReport) -> str:
    snapshot = report.snapshot
    agents = "\n".join(
        "| `{}` | {} | {} | {}% | {} |".format(
            item.role,
            item.status,
            item.stance,
            item.confidence,
            item.summary.replace("|", "/").replace("\n", " "),
        )
        for item in report.agents
    )
    missing = "\n".join(f"- {item}" for item in report.missing_data) or "- None reported"
    risks = "\n".join(f"- {item}" for item in report.key_risks) or "- None reported"
    invalidation = "\n".join(f"- {item}" for item in report.invalidation_conditions) or "- Not specified"
    context_sections = ", ".join(f"`{item}`" for item in report.research_context_sections) or "None"
    annualised = (
        f"{snapshot.annualised_volatility:.6f}"
        if snapshot.annualised_volatility is not None
        else "Not calculated (supply --bars-per-year)"
    )
    data_warnings = "\n".join(f"- {item}" for item in snapshot.data_warnings) or "- None"
    return f"""# MarketCouncil Research Brief — {report.symbol}

> **Research support only. Not investment advice or an executable trade instruction.**

- Generated: `{report.generated_at}`
- Symbol: `{report.symbol}`
- Question: {report.question}
- Research stance: **{report.stance}**
- Model-reported confidence: **{report.confidence}%** (not a calibrated probability)
- Review status: **{report.review_status}**
- Execution authorization: **{report.execution_authorization}**
- Research context attached: **{report.research_context_attached}**
- Context sections: {context_sections}

## Market data snapshot

| Field | Value |
|---|---:|
| Timeframe | {snapshot.timeframe} |
| Bars | {snapshot.bars_count} |
| Latest timestamp (UTC) | {snapshot.latest_timestamp} |
| Latest close | {snapshot.latest_close:.6f} |
| Lookback change | {snapshot.change_pct:.3f}% |
| Per-bar realised volatility | {snapshot.realised_volatility if snapshot.realised_volatility is not None else 'Not available'} |
| Annualised volatility | {annualised} |

### Data warnings

{data_warnings}

## Executive summary

{report.executive_summary}

## Thesis and scenarios

**Research thesis:** {report.thesis}

**Bull case:** {report.bull_case}

**Bear case:** {report.bear_case}

## Key risks and counter-evidence

{risks}

## Missing data

{missing}

## Invalidation conditions

{invalidation}

## Agent outputs

| Role | Status | Stance | Confidence | Summary |
|---|---|---|---:|---|
{agents}

## Human review gate

This run is a research artifact only. Verify source provenance, timestamps, market/session context, liquidity, transaction costs, account exposure, applicable rules, and relevant primary sources independently. Model-reported confidence is not a calibrated probability. **Execution authorization is NONE.**
"""
