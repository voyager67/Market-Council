#!/usr/bin/env python3
"""Generate the canonical JSON metadata index from portable SKILL.md files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "src/marketcouncil/skill_library"
TARGETS = (ROOT / "skills-index.json", ROOT / "src/marketcouncil/skill_index.json")


def parse_metadata(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: missing frontmatter")
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise ValueError(f"{path}: unterminated frontmatter") from exc
    result: dict[str, object] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"{path}: invalid metadata line")
        key, raw = line.split(":", 1)
        key, raw = key.strip(), raw.strip()
        if key in result:
            raise ValueError(f"{path}: duplicate metadata key {key}")
        if key == "asset_classes":
            if raw.startswith('"') and raw.endswith('"'):
                raw = str(json.loads(raw))
            value: object = [item.strip() for item in raw.split(",") if item.strip()]
        elif raw.startswith('"') and raw.endswith('"'):
            value = json.loads(raw)
        elif raw.isdigit():
            value = int(raw)
        else:
            value = raw
        result[key] = value
    return result


def build() -> dict[str, object]:
    skills: dict[str, object] = {}
    for skill_file in sorted(LIBRARY.glob("*/SKILL.md")):
        meta = parse_metadata(skill_file)
        name = str(meta.get("name", ""))
        if name != skill_file.parent.name:
            raise ValueError(f"{skill_file}: name must match directory")
        skills[name] = {
            "name": name,
            "description": meta.get("description", ""),
            "domain": meta.get("domain", ""),
            "asset_classes": meta.get("asset_classes", []),
            "path": f"skills/{name}/SKILL.md",
            "package_path": f"src/marketcouncil/skill_library/{name}/SKILL.md",
            "version": meta.get("version", 1),
        }
    if not skills:
        raise ValueError("no SKILL.md playbooks found")
    return {"schema_version": 1, "project": "MarketCouncil", "project_version": "1.0.0", "skills": skills}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if generated indexes are stale")
    args = parser.parse_args()
    expected = (json.dumps(build(), indent=2, ensure_ascii=False) + "\n").encode()
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path in TARGETS if not path.is_file() or path.read_bytes() != expected]
        if stale:
            print("Skill index is stale: " + ", ".join(stale))
            return 1
        print("Skill indexes are current")
        return 0
    for path in TARGETS:
        path.write_bytes(expected)
    print(f"Generated skill indexes for {len(json.loads(expected)['skills'])} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
