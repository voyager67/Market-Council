# Release process

This document defines the release checks for maintainers of the MarketCouncil repository.

## Release readiness

Before tagging a release:

- Confirm the version in `pyproject.toml` and the release notes in `CHANGELOG.md` agree.
- Review the complete diff for credentials, customer information, private market data, local databases and generated build artefacts.
- Run repository validation, generated-index checks, lint, tests, static security analysis, dependency auditing, package build and the offline demo.
- Confirm every required GitHub Actions matrix job passes.
- Review security and dependency findings and document accepted limitations.

## Reproducible checks

Run these commands from a clean checkout:

```bash
python -m pip install -e ".[dev,api,stream]"
python scripts/validate_repository.py
python scripts/build_skill_index.py --check
python scripts/build_skill_catalog.py --check
ruff check .
pytest -q
bandit -q -r src/marketcouncil
pip-audit
python -m build
market-council demo --format json
```

Build deterministic source archives with:

```bash
python scripts/package_source.py --output-dir ./release-artifacts
```

Verify the generated SHA-256 manifest after copying or downloading release artefacts. Never commit populated environment files, private keys, database files, local datasets or account exports.

## Version and release assets

Use a version tag in the form `vMAJOR.MINOR.PATCH`. Create release notes from the corresponding `CHANGELOG.md` entry. Attach the source ZIP, source TAR.GZ, Python wheel and checksum manifest only after those artefacts have been produced and verified.

The release description must state the implemented scope accurately. MarketCouncil provides research workflows, optional market-data integrations, a single-instrument OHLCV backtester, and paper/testnet adapters. It does not include live-money order routing or guarantee research accuracy, fills or trading performance.

## Post-release review

After publishing, verify the release page contains the intended tag and assets, checksums match, and the README's local images and video links render. Record release-specific limitations and continue dependency and security maintenance.
