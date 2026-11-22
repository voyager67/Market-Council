# Portable Trading Skills

This directory contains the 74 standalone `SKILL.md` playbooks shipped with MarketCouncil. These Markdown instructions are portable to compatible AI agent runtimes. They are not executable code, live market-data connectors, investment signals, or a performance guarantee.

`skills-index.json` at the repository root lists each skill's canonical metadata and package location. The repository validator checks each `skills/<id>/SKILL.md` file against its packaged counterpart under `src/marketcouncil/skill_library/<id>/SKILL.md`.
