#!/usr/bin/env python3
"""Build the human-readable skill catalogue from canonical JSON metadata."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketcouncil.agents import ROLE_SKILLS  # noqa: E402

INDEX = ROOT / "skills-index.json"
TARGET = ROOT / "docs/SKILL_CATALOG.md"


def render() -> str:
    payload = json.loads(INDEX.read_text(encoding="utf-8"))
    lines = [
        "# Complete Trader Skill Catalogue",
        "",
        "The authoritative skill index is [`../skills-index.json`](../skills-index.json). "
        "There are 74 portable `SKILL.md` playbooks. Every skill is a prompt/playbook resource, "
        "not executable code or a verified data feed.",
        "",
        "| Skill ID | Domain | Asset classes | Assigned roles |",
        "|---|---|---|---|",
    ]
    for skill_id, item in sorted(payload["skills"].items()):
        asset_classes = item.get("asset_classes", [])
        if isinstance(asset_classes, str):
            asset_classes = [asset_classes]
        roles = [role for role, skills in ROLE_SKILLS.items() if skill_id in skills]
        lines.append(
            f"| `{skill_id}` | {item.get('domain', '')} | "
            f"{', '.join(asset_classes)} | {', '.join(roles)} |"
        )
    lines.extend(
        [
            "",
            "## Using the catalogue",
            "",
            "Use `market-council skills list`, `market-council skills search`, and "
            "`market-council skills show <skill-id>` to explore the playbooks. "
            "The JSON index is canonical; this Markdown file is generated for browsing.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the catalogue is stale")
    args = parser.parse_args()
    expected = render()
    if args.check:
        actual = TARGET.read_text(encoding="utf-8") if TARGET.exists() else ""
        if actual != expected:
            print("Skill catalogue is stale; run python scripts/build_skill_catalog.py")
            return 1
        print("Skill catalogue is current")
        return 0
    TARGET.write_text(expected, encoding="utf-8")
    print("Generated Markdown catalogue for 74 trader skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
