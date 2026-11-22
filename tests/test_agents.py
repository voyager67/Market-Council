from datetime import UTC, datetime, timedelta
import json

import pytest

from marketcouncil.agents import AGENT_ROLES, model_for_role, parse_agent_output, run_agent
from marketcouncil.metrics import build_snapshot
from marketcouncil.models import Bar
from marketcouncil.providers import MockProvider


def snapshot():
    rows = []
    now = datetime(2026, 1, 1, tzinfo=UTC)
    for i, close in enumerate((100.0, 101.0, 102.0)):
        rows.append(Bar(now + timedelta(days=i), close, close + 1, close - 1, close, 1000))
    return build_snapshot("DEMO", "1d", rows, bars_per_year=252)


def valid_payload(**overrides):
    value = {
        "stance": "NEUTRAL",
        "confidence": 50,
        "summary": "A valid observation.",
        "evidence": [],
        "counter_evidence": [],
        "missing_data": [],
        "invalidation": [],
    }
    value.update(overrides)
    return json.dumps(value)


def test_agent_roles_are_defined():
    assert len(AGENT_ROLES) == 15
    assert "bull_researcher" in AGENT_ROLES
    assert "bear_researcher" in AGENT_ROLES


def test_parser_accepts_valid_schema():
    result = parse_agent_output("technical_analyst", valid_payload())
    assert result.stance == "NEUTRAL"
    assert result.confidence == 50


@pytest.mark.parametrize(
    "raw",
    [
        "not json",
        valid_payload(stance="BUY"),
        valid_payload(confidence=101),
        valid_payload(confidence=True),
        valid_payload(summary="  "),
        valid_payload(evidence="not-a-list"),
    ],
)
def test_parser_rejects_invalid_output(raw):
    with pytest.raises(ValueError):
        parse_agent_output("technical_analyst", raw)


def test_live_model_mapping_is_read_from_environment(monkeypatch):
    monkeypatch.setenv("MC_AGENT_MODELS", '{"technical_analyst":"provider/model-a"}')
    assert model_for_role("technical_analyst", "fallback") == "provider/model-a"
    assert model_for_role("bear_researcher", "fallback") == "fallback"


def test_invalid_model_mapping_is_rejected(monkeypatch):
    monkeypatch.setenv("MC_AGENT_MODELS", "not-json")
    with pytest.raises(ValueError, match="valid JSON"):
        model_for_role("technical_analyst")


def test_mock_provider_completes_technical_role():
    result = run_agent(
        role="technical_analyst", snapshot=snapshot(), question="Inspect structure", provider=MockProvider()
    )
    assert result.status == "COMPLETED"
    assert result.stance in {"BULLISH", "BEARISH", "NEUTRAL"}


class BrokenProvider:
    def complete(self, *, prompt, model=None):
        raise RuntimeError("token=should-not-leak")


def test_provider_exception_fails_closed_without_echoing_message():
    result = run_agent(
        role="technical_analyst", snapshot=snapshot(), question="Test", provider=BrokenProvider()
    )
    assert result.status == "ABSTAINED"
    assert result.stance == "ABSTAIN"
    assert result.error == "RuntimeError"
    assert "should-not-leak" not in json.dumps(result.to_dict())


def test_agent_prompt_includes_role_specific_skill_playbooks():
    class RecordingProvider:
        prompt = ""

        def complete(self, *, prompt, model=None):
            self.prompt = prompt
            return valid_payload()

    provider = RecordingProvider()
    run_agent(
        role="technical_analyst",
        snapshot=snapshot(),
        question="Inspect trend",
        provider=provider,
    )
    prompt = json.loads(provider.prompt)
    assert [item["name"] for item in prompt["skill_playbooks"]] == list(
        __import__("marketcouncil.agents", fromlist=["ROLE_SKILLS"]).ROLE_SKILLS["technical_analyst"]
    )
    assert "## Guardrails" in prompt["skill_playbooks"][0]["instructions"]


def test_provider_default_model_is_recorded_when_role_has_no_override():
    class NamedProvider:
        default_model = "vendor/model-default"

        def complete(self, *, prompt, model=None):
            return valid_payload()

    result = run_agent(
        role="technical_analyst",
        snapshot=snapshot(),
        question="Inspect",
        provider=NamedProvider(),
    )
    assert result.model == "vendor/model-default"


def test_agent_roster_has_specialists_for_multiple_trading_domains():
    assert len(AGENT_ROLES) == 15
    assert "derivatives_analyst" in AGENT_ROLES
    assert "crypto_analyst" in AGENT_ROLES
    assert "institutional_flow_analyst" in AGENT_ROLES
    assert "synthesis_director" == AGENT_ROLES[-1]


def test_all_agent_skill_routes_resolve_to_existing_playbooks():
    from marketcouncil.agents import ROLE_SKILLS
    from marketcouncil.skills import list_skills

    known = {name for name, _ in list_skills()}
    assert set(ROLE_SKILLS) == set(AGENT_ROLES)
    assert all(skill in known for skills in ROLE_SKILLS.values() for skill in skills)


def test_synthesis_parser_requires_structured_thesis_fields():
    payload = {
        "stance": "INSUFFICIENT_DATA",
        "confidence": 0,
        "summary": "Insufficient evidence.",
        "thesis": "No validated thesis.",
        "bull_case": "Conditional upside only.",
        "bear_case": "Downside remains possible.",
        "key_risks": ["Missing source data"],
        "evidence": [],
        "counter_evidence": [],
        "missing_data": ["Primary sources"],
        "invalidation": [],
    }
    result = parse_agent_output("synthesis_director", json.dumps(payload))
    assert result.thesis == "No validated thesis."
    assert result.key_risks == ("Missing source data",)
    with pytest.raises(ValueError, match="requires thesis"):
        parse_agent_output("synthesis_director", valid_payload(stance="INSUFFICIENT_DATA"))


def test_model_map_rejects_unknown_agent_roles(monkeypatch):
    monkeypatch.setenv("MC_AGENT_MODELS", '{"unregistered":"vendor/model"}')
    with pytest.raises(ValueError, match="unknown roles"):
        model_for_role("technical_analyst")


def test_every_skill_is_routed_to_a_specialist():
    from marketcouncil.agents import ROLE_SKILLS
    from marketcouncil.skills import list_skills

    all_skills = {name for name, _description in list_skills()}
    routed = {skill for skills in ROLE_SKILLS.values() for skill in skills}
    assert routed == all_skills
