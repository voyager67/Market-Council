# Contributing

Contributions should make trading research more correct, auditable, secure, and maintainable—not simply add more agents or prompts.

## Before contributing

1. Read [Architecture](docs/ARCHITECTURE.md), [Risk and Validation](docs/RISK_AND_VALIDATION.md), and [Operating Model](docs/OPERATING_MODEL.md).
2. Keep provider-specific logic behind `LLMProvider`.
3. Keep deterministic arithmetic and hard safety boundaries outside model output.
4. Add tests for input boundaries, failure modes, and important edge cases.
5. Label synthetic data and illustrative media explicitly.
6. Do not commit credentials, private customer data, brokerage exports, or external skill text/code without explicit rights and appropriate notices.
7. Do not claim performance improvements without reproducible, bias-aware evaluation.

## Development checks

```bash
python -m pip install -e ".[dev]"
python scripts/validate_repository.py
ruff check .
pytest -q
market-council demo --format json
```

## Skill authoring contract

Every playbook must be a `skills/<skill-id>/SKILL.md` file mirrored byte-for-byte under `src/marketcouncil/skill_library/<skill-id>/SKILL.md`. Required frontmatter fields: `name`, `description`, `domain`, `version`, `asset_classes`, and `source_basis`. Required sections: Purpose, Required inputs, Procedure, Expected output, Guardrails, Evidence standard, and Research references. Use concise, operational language. Require source timestamps and units where they matter; explicitly abstain when evidence is missing; never promise profitable outcomes.

Update `skills-index.json` and its packaged copy when adding/removing skills. Update relevant `ROLE_SKILLS`, workflows, and skillsets. Run the repository validator before submitting.
