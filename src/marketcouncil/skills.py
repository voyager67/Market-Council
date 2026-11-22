"""Discover, search, read, and validate the bundled Markdown skill playbooks."""

from __future__ import annotations

import json
import re
from importlib.resources import files
from typing import Any

SKILL_ROOT = files("marketcouncil").joinpath("skill_library")
REQUIRED_METADATA = ("name", "description", "domain", "asset_classes", "version", "source_basis")
REQUIRED_SECTIONS = (
    "## Purpose",
    "## Required inputs",
    "## Procedure",
    "## Expected output",
    "## Guardrails",
    "## Evidence standard",
    "## Research references",
)


def _parse_frontmatter(content: str) -> dict[str, Any]:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing YAML frontmatter opener")
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as exc:
        raise ValueError("missing YAML frontmatter closer") from exc
    metadata: dict[str, Any] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line}")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if not key or key in metadata:
            raise ValueError(f"empty or duplicate frontmatter key: {key!r}")
        if value.startswith('"') and value.endswith('"'):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid quoted frontmatter value for {key}") from exc
        elif value.isdigit():
            value = int(value)
        metadata[key] = value
    return metadata


def get_skill_metadata(name: str) -> dict[str, Any]:
    if not name or "/" in name or "\\" in name or name in {".", ".."}:
        raise ValueError("invalid skill name")
    skill_file = SKILL_ROOT.joinpath(name, "SKILL.md")
    if not skill_file.is_file():
        raise FileNotFoundError(f"unknown skill: {name}")
    return _parse_frontmatter(skill_file.read_text(encoding="utf-8"))


def list_skills() -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []
    if not SKILL_ROOT.is_dir():
        return results
    for folder in sorted(SKILL_ROOT.iterdir(), key=lambda item: item.name):
        if not folder.is_dir():
            continue
        skill_file = folder.joinpath("SKILL.md")
        if not skill_file.is_file():
            continue
        metadata = _parse_frontmatter(skill_file.read_text(encoding="utf-8"))
        results.append((folder.name, str(metadata.get("description", ""))))
    return results


def read_skill(name: str) -> str:
    if not name or "/" in name or "\\" in name or name in {".", ".."}:
        raise ValueError("invalid skill name")
    candidate = SKILL_ROOT.joinpath(name, "SKILL.md")
    if not candidate.is_file():
        raise FileNotFoundError(f"unknown skill: {name}")
    return candidate.read_text(encoding="utf-8")


def search_skills(query: str) -> list[tuple[str, str]]:
    terms = [term for term in re.findall(r"[a-z0-9_-]+", query.lower()) if term]
    if not terms:
        return []
    matches = []
    for name, description in list_skills():
        metadata = get_skill_metadata(name)
        content = read_skill(name).lower()
        haystack = " ".join(
            [name, description, str(metadata.get("domain", "")), str(metadata.get("asset_classes", "")), content]
        ).lower()
        score = sum(term in haystack for term in terms)
        if score:
            matches.append((score, name, description))
    matches.sort(key=lambda item: (-item[0], item[1]))
    return [(name, description) for _, name, description in matches]


def validate_skill_library() -> list[str]:
    errors: list[str] = []
    if not SKILL_ROOT.is_dir():
        return ["skill_library directory is missing"]
    seen: set[str] = set()
    for folder in sorted(SKILL_ROOT.iterdir(), key=lambda item: item.name):
        if not folder.is_dir():
            continue
        skill_file = folder.joinpath("SKILL.md")
        if not skill_file.is_file():
            errors.append(f"{folder.name}: missing SKILL.md")
            continue
        try:
            content = skill_file.read_text(encoding="utf-8")
            metadata = _parse_frontmatter(content)
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"{folder.name}: invalid metadata: {type(exc).__name__}: {exc}")
            continue
        missing = [field for field in REQUIRED_METADATA if not metadata.get(field)]
        if missing:
            errors.append(f"{folder.name}: missing metadata fields: {', '.join(missing)}")
        if metadata.get("name") != folder.name:
            errors.append(f"{folder.name}: metadata name does not match folder")
        if folder.name in seen:
            errors.append(f"{folder.name}: duplicate skill identifier")
        seen.add(folder.name)
        if metadata.get("version") != 1:
            errors.append(f"{folder.name}: unsupported skill version")
        for section in REQUIRED_SECTIONS:
            if section not in content:
                errors.append(f"{folder.name}: missing section {section}")
        if len(content) < 700:
            errors.append(f"{folder.name}: playbook is unexpectedly short")
    if len(seen) < 1:
        errors.append("no valid skill playbooks found")
    return errors
