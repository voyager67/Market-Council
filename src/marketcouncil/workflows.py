"""Read and validate machine-readable trader workflow manifests."""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Any

from .agents import AGENT_ROLES
from .skills import list_skills

WORKFLOW_ROOT = files("marketcouncil").joinpath("workflows")


def list_workflows() -> list[tuple[str, str]]:
    found = []
    if not WORKFLOW_ROOT.is_dir():
        return found
    for entry in sorted(WORKFLOW_ROOT.iterdir(), key=lambda item: item.name):
        if entry.name.endswith(".json") and entry.name != "index.json" and entry.is_file():
            payload = json.loads(entry.read_text(encoding="utf-8"))
            found.append((payload["id"], payload["title"]))
    return found


def read_workflow(name: str) -> dict[str, Any]:
    if not name or "/" in name or "\\" in name or name in {".", ".."}:
        raise ValueError("invalid workflow identifier")
    path = WORKFLOW_ROOT.joinpath(f"{name}.json")
    if not path.is_file():
        raise FileNotFoundError(f"unknown workflow: {name}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_workflows() -> list[str]:
    errors: list[str] = []
    identifiers: set[str] = set()
    for name, _title in list_workflows():
        try:
            payload = read_workflow(name)
        except (ValueError, json.JSONDecodeError, FileNotFoundError) as exc:
            errors.append(f"{name}: {type(exc).__name__}: {exc}")
            continue
        if payload.get("schema_version") != 1:
            errors.append(f"{name}: unsupported schema_version")
        if payload.get("id") != name:
            errors.append(f"{name}: id does not match filename")
        if name in identifiers:
            errors.append(f"{name}: duplicate workflow id")
        identifiers.add(name)
        for required in ("title", "objective", "asset_classes", "required_inputs", "steps", "decision_gates"):
            if not payload.get(required):
                errors.append(f"{name}: missing {required}")
        if payload.get("human_review_required") is not True:
            errors.append(f"{name}: human_review_required must be true")
        if payload.get("execution_authorization") != "NONE":
            errors.append(f"{name}: execution_authorization must be NONE")
        if not isinstance(payload.get("steps"), list):
            errors.append(f"{name}: steps must be an array")
            continue
        known_skills = {skill_name for skill_name, _ in list_skills()}
        for step_index, step in enumerate(payload["steps"]):
            if not isinstance(step, dict):
                errors.append(f"{name}: step {step_index} must be an object")
                continue
            role = step.get("agent_role")
            if role not in AGENT_ROLES:
                errors.append(f"{name}: step {step_index} has unknown agent role {role!r}")
            for skill_name in step.get("skills", []):
                if skill_name not in known_skills:
                    errors.append(f"{name}: step {step_index} has unknown skill {skill_name!r}")
    return errors
