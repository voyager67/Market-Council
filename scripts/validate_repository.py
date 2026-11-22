#!/usr/bin/env python3
"""Validate skill, workflow, skillset, package, and documentation contracts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketcouncil.agents import AGENT_ROLES, ROLE_SKILLS  # noqa: E402
from marketcouncil.skills import get_skill_metadata, list_skills, validate_skill_library  # noqa: E402
from marketcouncil.workflows import validate_workflows  # noqa: E402


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_skill_index(errors: list[str], skill_names: set[str]) -> None:
    for path in (ROOT / "skills-index.json", ROOT / "src/marketcouncil/skill_index.json"):
        if not path.is_file():
            errors.append(f"missing skill index: {path.relative_to(ROOT)}")
            continue
        try:
            payload = read_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid skill index {path.relative_to(ROOT)}: {type(exc).__name__}")
            continue
        indexed = set(payload.get("skills", {}))
        if payload.get("schema_version") != 1:
            errors.append(f"unsupported skill index schema: {path.relative_to(ROOT)}")
        if indexed != skill_names:
            errors.append(f"skill index does not match playbooks: {path.relative_to(ROOT)}")
        for name in indexed & skill_names:
            item = payload.get("skills", {}).get(name, {})
            metadata = get_skill_metadata(name)
            classes = [part.strip() for part in str(metadata.get("asset_classes", "")).split(",") if part.strip()]
            for field in ("description", "domain", "version"):
                if item.get(field) != metadata.get(field):
                    errors.append(f"skill index metadata mismatch for {name}: {field}")
            if item.get("asset_classes") != classes:
                errors.append(f"skill index asset classes mismatch for {name}")
    root_index = ROOT / "skills-index.json"
    package_index = ROOT / "src/marketcouncil/skill_index.json"
    if root_index.is_file() and package_index.is_file() and root_index.read_bytes() != package_index.read_bytes():
        errors.append("root and packaged skill indexes differ")



def validate_skill_mirror(errors: list[str], skill_names: set[str]) -> None:
    portable = ROOT / "skills"
    if not portable.is_dir():
        errors.append("missing portable root skills directory")
        return
    portable_names = {
        path.parent.name for path in portable.glob("*/SKILL.md")
    }
    if portable_names != skill_names:
        errors.append("portable root skills directory does not match packaged skill library")
    for name in sorted(skill_names & portable_names):
        root_file = portable / name / "SKILL.md"
        package_file = ROOT / "src/marketcouncil/skill_library" / name / "SKILL.md"
        if root_file.read_bytes() != package_file.read_bytes():
            errors.append(f"portable and packaged skill differ: {name}")


def validate_skill_routes(errors: list[str], skill_names: set[str]) -> None:
    if set(ROLE_SKILLS) != set(AGENT_ROLES):
        errors.append("agent-to-skill mapping does not cover the complete agent roster")
    routed: set[str] = set()
    for role, skills in ROLE_SKILLS.items():
        for skill in skills:
            routed.add(skill)
            if skill not in skill_names:
                errors.append(f"agent {role} references missing skill {skill}")
    if routed != skill_names:
        errors.append(f"agent mappings do not cover complete skill library (unmapped={sorted(skill_names-routed)})")


def validate_skillsets(errors: list[str], skill_names: set[str]) -> None:
    root = ROOT / "skillsets"
    package = ROOT / "src/marketcouncil/skillsets"
    for folder in (root, package):
        if not folder.is_dir():
            errors.append(f"missing skillsets directory: {folder.relative_to(ROOT)}")
            continue
        for path in sorted(folder.glob("*.json")):
            if path.name == "index.json":
                continue
            try:
                payload = read_json(path)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"invalid skillset {path.relative_to(ROOT)}: {type(exc).__name__}")
                continue
            if payload.get("id") != path.stem or payload.get("schema_version") != 1:
                errors.append(f"invalid skillset identity/schema: {path.relative_to(ROOT)}")
            for tier in ("required_skills", "recommended_skills", "optional_skills"):
                values = payload.get(tier, [])
                if not isinstance(values, list) or len(values) != len(set(values)):
                    errors.append(f"skillset {payload.get('id')} has an invalid {tier} list")
                    continue
                for name in values:
                    if name not in skill_names:
                        errors.append(f"skillset {payload.get('id')} references missing skill {name}")
            for name in payload.get("related_workflows", []):
                if not (ROOT / "workflows" / f"{name}.json").is_file():
                    errors.append(f"skillset {payload.get('id')} references missing workflow {name}")
    root_names = {p.name for p in root.glob("*.json")}
    package_names = {p.name for p in package.glob("*.json")}
    if root_names != package_names:
        errors.append("root and packaged skillset manifest file sets differ")
    for name in root_names & package_names:
        if (root / name).read_bytes() != (package / name).read_bytes():
            errors.append(f"root and packaged skillset differ: {name}")
    used = set()
    for path in root.glob("*.json"):
        if path.name == "index.json":
            continue
        payload = read_json(path)
        for tier in ("required_skills", "recommended_skills", "optional_skills"):
            used.update(payload.get(tier, []))
    if used != skill_names:
        errors.append(f"skillsets do not cover complete library (missing={sorted(skill_names-used)}, unknown={sorted(used-skill_names)})")


def validate_workflow_copies(errors: list[str]) -> None:
    root = ROOT / "workflows"
    package = ROOT / "src/marketcouncil/workflows"
    root_files = {p.name for p in root.glob("*.json")}
    package_files = {p.name for p in package.glob("*.json")}
    if root_files != package_files:
        errors.append("root and packaged workflow manifest file sets differ")
    for name in root_files & package_files:
        if (root / name).read_bytes() != (package / name).read_bytes():
            errors.append(f"root and packaged workflow differ: {name}")


def validate_markdown_links(errors: list[str]) -> int:
    count = 0
    pattern = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
    for markdown in ROOT.rglob("*.md"):
        if any(part in {".venv", "build", "dist", ".pytest_cache", "__pycache__"} or part.endswith(".egg-info") for part in markdown.parts):
            continue
        text = markdown.read_text(encoding="utf-8")
        for raw_target in pattern.findall(text):
            target = raw_target.strip().split()[0].strip("<>")
            if not target or target.startswith(("https://", "http://", "mailto:", "data:")):
                continue
            local_path = target.split("#", 1)[0]
            if not local_path:
                continue
            count += 1
            resolved = (markdown.parent / local_path).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"link escapes repository in {markdown.relative_to(ROOT)}: {target}")
                continue
            if not resolved.exists():
                errors.append(f"broken local link in {markdown.relative_to(ROOT)}: {target}")
    return count


def validate_secrets(errors: list[str]) -> int:
    checked = 0
    secret_patterns = [
        re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
        re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b"),
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        re.compile(r"\bsk-[A-Za-z0-9]{32,}\b"),
    ]
    forbidden_names = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in {".git", ".venv", "build", "dist", ".pytest_cache", "__pycache__"} or part.endswith(".egg-info") for part in path.parts):
            continue
        if path.name in forbidden_names or path.suffix.lower() in {".pem", ".p12", ".pfx", ".key"}:
            errors.append(f"potential secret/private-key file present: {path.relative_to(ROOT)}")
            continue
        if path.suffix.lower() not in {".py", ".md", ".json", ".yaml", ".yml", ".toml", ".txt", ".ini", ".cfg"}:
            continue
        try:
            data = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        checked += 1
        for pattern in secret_patterns:
            if pattern.search(data):
                errors.append(f"potential credential pattern in {path.relative_to(ROOT)}")
                break
    return checked


def main() -> int:
    errors: list[str] = []
    skill_errors = validate_skill_library()
    errors.extend(f"skill: {item}" for item in skill_errors)
    workflow_errors = validate_workflows()
    errors.extend(f"workflow: {item}" for item in workflow_errors)
    skills = list_skills()
    names = {name for name, _ in skills}
    validate_skill_index(errors, names)
    validate_skill_mirror(errors, names)
    validate_skill_routes(errors, names)
    validate_skillsets(errors, names)
    validate_workflow_copies(errors)
    markdown_links = validate_markdown_links(errors)
    scanned_files = validate_secrets(errors)

    if errors:
        print("Repository validation FAILED")
        for item in errors:
            print(f"- {item}")
        return 1
    print("Repository validation PASSED")
    print(f"Skills: {len(skills)}")
    print(f"Agent roles: {len(AGENT_ROLES)}")
    print(f"Workflows: {len(list((ROOT / 'workflows').glob('*.json'))) - 1}")
    print(f"Skillsets: {len(list((ROOT / 'skillsets').glob('*.json'))) - 1}")
    print(f"Local Markdown links checked: {markdown_links}")
    print(f"Text/config files scanned for common secret patterns: {scanned_files}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
