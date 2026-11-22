from datetime import UTC, datetime, timedelta

import pytest

from marketcouncil.agents import AGENT_ROLES
from marketcouncil.metrics import build_snapshot
from marketcouncil.models import Bar
from marketcouncil.orchestrator import run_council
from marketcouncil.providers import MockProvider
from marketcouncil.report import render_json, render_markdown
from marketcouncil.skills import list_skills, read_skill


def make_snapshot():
    start = datetime(2026, 1, 1, tzinfo=UTC)
    rows = [
        Bar(start + timedelta(days=i), c, c + 1, c - 1, c, 1000 + i)
        for i, c in enumerate((100, 101, 102, 101, 103))
    ]
    return build_snapshot("DEMO", "1d", rows, bars_per_year=252)


def test_offline_council_returns_all_roles_and_human_gate():
    report = run_council(
        snapshot=make_snapshot(), question="Review the supplied data", provider=MockProvider()
    )
    assert tuple(agent.role for agent in report.agents) == AGENT_ROLES
    assert report.review_status == "HUMAN_REVIEW_REQUIRED"
    assert report.execution_authorization == "NONE"
    assert report.stance == "INSUFFICIENT_DATA"
    assert any(agent.status == "ABSTAINED" for agent in report.agents)


def test_rejects_invalid_worker_count():
    with pytest.raises(ValueError, match="max_workers"):
        run_council(
            snapshot=make_snapshot(), question="Review", provider=MockProvider(), max_workers=0
        )


def test_rejects_empty_question():
    with pytest.raises(ValueError, match="question"):
        run_council(snapshot=make_snapshot(), question=" ", provider=MockProvider())


def test_report_formats_keep_execution_authorization_none():
    report = run_council(
        snapshot=make_snapshot(), question="Review", provider=MockProvider()
    )
    assert '"execution_authorization": "NONE"' in render_json(report)
    assert "Execution authorization: **NONE**" in render_markdown(report)


def test_skill_playbooks_and_metadata_sections():
    skills = list_skills()
    assert len(skills) == 74
    for name, description in skills:
        assert description
        content = read_skill(name)
        assert content.startswith("---\n")
        for section in ("## Purpose", "## Required inputs", "## Procedure", "## Expected output", "## Guardrails", "## Evidence standard", "## Research references"):
            assert section in content
        assert f"name: {name}" in content


def test_skill_reader_blocks_path_traversal():
    with pytest.raises(ValueError):
        read_skill("../README")
    with pytest.raises(FileNotFoundError):
        read_skill("not-a-real-skill")


def test_expanded_council_returns_fifteen_roles_and_no_execution():
    report = run_council(
        snapshot=make_snapshot(), question="Review", provider=MockProvider()
    )
    assert len(report.agents) == 15
    assert report.agents[-1].role == "synthesis_director"
    assert report.execution_authorization == "NONE"
    assert report.research_context_attached is False


def test_context_metadata_is_reported_and_passed_to_agents():
    context = {
        "fundamentals": {"currency": "USD", "period": "FY2025"},
        "sources": [{"publisher": "Example Issuer", "uri": "https://example.invalid/filing"}],
    }
    report = run_council(
        snapshot=make_snapshot(),
        question="Review supplied context",
        provider=MockProvider(),
        research_context=context,
    )
    assert report.research_context_attached is True
    assert report.research_context_sections == ("fundamentals", "sources")


def test_all_skill_playbooks_have_reference_and_domain_sections():
    from marketcouncil.skills import validate_skill_library

    assert len(list_skills()) == 74
    assert validate_skill_library() == []
    for name, _description in list_skills():
        content = read_skill(name)
        assert "## Research references" in content
        assert "## Evidence standard" in content


def test_invalid_agent_model_routing_fails_before_council_execution(monkeypatch):
    monkeypatch.setenv("MC_AGENT_MODELS", '{"unknown_role":"provider/model"}')
    with pytest.raises(ValueError, match="unknown roles"):
        run_council(
            snapshot=make_snapshot(), question="Review", provider=MockProvider()
        )
