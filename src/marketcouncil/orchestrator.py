"""Bounded parallel council orchestration with sequential final synthesis."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from typing import Any

from .agents import (
    ADVERSARIAL_ANALYSTS,
    AGENT_ROLES,
    DOMAIN_ANALYSTS,
    run_agent,
    validate_model_routing,
)
from .models import AgentReport, CouncilReport, MarketSnapshot
from .providers import LLMProvider

MAX_AGENT_WORKERS = 16


def run_council(
    *,
    snapshot: MarketSnapshot,
    question: str,
    provider: LLMProvider,
    max_workers: int = 8,
    fallback_model: str | None = None,
    research_context: dict[str, Any] | None = None,
) -> CouncilReport:
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question cannot be empty")
    if max_workers < 1 or max_workers > MAX_AGENT_WORKERS:
        raise ValueError(f"max_workers must be between 1 and {MAX_AGENT_WORKERS}")
    if research_context is not None and not isinstance(research_context, dict):
        raise ValueError("research_context must be a JSON object")
    validate_model_routing()

    reports_by_role: dict[str, AgentReport] = {}
    parallel_roles = (*DOMAIN_ANALYSTS, *ADVERSARIAL_ANALYSTS)
    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="mc-agent") as pool:
        futures = {
            pool.submit(
                run_agent,
                role=role,
                snapshot=snapshot,
                question=question,
                provider=provider,
                research_context=research_context,
                fallback_model=fallback_model,
            ): role
            for role in parallel_roles
        }
        for future in as_completed(futures):
            role = futures[future]
            reports_by_role[role] = future.result()

    upstream = [reports_by_role[role].to_dict() for role in parallel_roles]
    synthesis = run_agent(
        role="synthesis_director",
        snapshot=snapshot,
        question=question,
        provider=provider,
        upstream_reports=upstream,
        research_context=research_context,
        fallback_model=fallback_model,
    )
    reports_by_role["synthesis_director"] = synthesis
    ordered = tuple(reports_by_role[role] for role in AGENT_ROLES)
    missing = sorted({gap for report in ordered for gap in report.missing_data})

    if synthesis.status == "ABSTAINED":
        stance = "INSUFFICIENT_DATA"
        summary = "The synthesis agent abstained; human review of the individual reports is required."
        thesis = "No validated synthesis is available from this run."
        bull = next((r.summary for r in ordered if r.role == "bull_researcher"), "Not available")
        bear = next((r.summary for r in ordered if r.role == "bear_researcher"), "Not available")
        risks = ("Synthesis output failed validation",)
        invalidation = ("Re-run only after reviewing provider output and evidence quality",)
        confidence = 0
    else:
        stance = synthesis.stance
        summary = synthesis.summary
        thesis = synthesis.thesis or "No additional thesis was supplied."
        bull = synthesis.bull_case or next(
            (r.summary for r in ordered if r.role == "bull_researcher"), "Not available"
        )
        bear = synthesis.bear_case or next(
            (r.summary for r in ordered if r.role == "bear_researcher"), "Not available"
        )
        risks = synthesis.key_risks or tuple(
            item for report in ordered for item in report.counter_evidence
        )[:12] or ("Evidence coverage is limited; review source quality",)
        invalidation = tuple(item for report in ordered for item in report.invalidation)[:20]
        confidence = synthesis.confidence

    return CouncilReport(
        generated_at=datetime.now(UTC).isoformat(),
        symbol=snapshot.symbol,
        question=question.strip(),
        snapshot=snapshot,
        stance=stance,
        confidence=confidence,
        executive_summary=summary,
        thesis=thesis,
        bull_case=bull,
        bear_case=bear,
        key_risks=tuple(risks),
        missing_data=tuple(missing),
        invalidation_conditions=tuple(invalidation),
        agents=ordered,
        review_status="HUMAN_REVIEW_REQUIRED",
        execution_authorization="NONE",
        research_context_attached=bool(research_context),
        research_context_sections=tuple(sorted(research_context or {})),
    )
