# Publishing MarketCouncil 1.0.0

This source archive is prepared for publication, but it is **not yet hosted on GitHub**. The connected GitHub workspace had no existing MarketCouncil repository, and the available GitHub actions do not create a new repository. A repository owner must create the empty repository and push this source tree.

## Suggested GitHub repository settings

- **Repository name:** `MarketCouncil` (or `market-council` if preferred)
- **Visibility:** Public, if you intend to build an open-source trader community
- **Description:** `Multi-agent trading research platform with 74 trader skills, REST and WebSocket market data, historical backtesting, paper trading, and risk-focused workflows.`
- **Website:** leave blank until a documentation site or project website is actually deployed
- **Topics:** `trading`, `algorithmic-trading`, `quantitative-finance`, `multi-agent-systems`, `llm-agents`, `market-research`, `technical-analysis`, `risk-management`, `portfolio-management`, `options-trading`, `futures-trading`, `crypto-trading`, `python`, `litellm`
- **License:** MIT (the `LICENSE` file is already included)
- **Default branch:** `main`

Do not add a second README, license, or `.gitignore` during repository creation. This archive already contains them.

## 1. Create the empty GitHub repository

On GitHub, choose **New repository**, enter the name above, select Public or Private according to your release decision, and leave **Add a README**, **Add .gitignore**, and **Choose a license** unchecked. Create the empty repository.

## 2. Push the source tree from Windows PowerShell

Install Git for Windows if `git --version` is not recognised. Download `MarketCouncil-1.0.0-FINAL.zip` from the prepared handoff, then run the following commands (adjust the download location and GitHub owner/repository URL):

```powershell
$ProjectRoot = Join-Path $HOME "Projects"
New-Item -ItemType Directory -Force -Path $ProjectRoot | Out-Null
Expand-Archive -LiteralPath (Join-Path $HOME "Downloads\MarketCouncil-1.0.0-FINAL.zip") -DestinationPath $ProjectRoot -Force
Set-Location (Join-Path $ProjectRoot "market-council")

git init -b main
git add --all
git status --short
git commit -m "Release MarketCouncil 1.0.0"
git remote add origin https://github.com/<YOUR_GITHUB_OWNER>/<YOUR_REPOSITORY>.git
git push -u origin main
```

Replace the angle-bracket placeholders with the repository owner and exact repository name. Review `git status --short` before committing. Never add API keys, private market data, account exports, `.env` files, or customer information.

## 3. Verify the first hosted CI run

After pushing, open the repository's **Actions** tab. The included workflow runs on Python 3.11, 3.12, and 3.13. Confirm that all matrix jobs pass. If a job fails, fix the source and rerun the checks before publishing a release tag. Ruff is part of hosted CI; it was not available in the offline build environment used to prepare this archive.

## 4. Publish the single final release

After the first hosted CI run is green:

1. Open **Releases → Draft a new release**.
2. Create tag `v1.0.0` on branch `main`.
3. Use title `MarketCouncil 1.0.0 — Final`.
4. Attach `MarketCouncil-1.0.0-FINAL.zip`, `MarketCouncil-1.0.0-FINAL.tar.gz`, `marketcouncil-1.0.0-py3-none-any.whl`, and `MarketCouncil-1.0.0-SHA256SUMS.txt`.
5. Copy the release notes from `CHANGELOG.md` and publish.

The project is marked as the final consolidated snapshot for this brief. Describe the implemented REST market-data snapshots, read-only WebSocket tick streams, single-instrument backtester, local paper simulator, Alpaca Paper and Binance Spot Testnet LIMIT adapters accurately. Do not imply automatic stream recovery, tick persistence, venue-grade backtesting, or live-money execution. Do not promise that no security fixes will ever be needed; "final" describes the planned feature/release scope, not a guarantee that software never requires maintenance.

## 5. Post-publication checks

- Confirm the repository homepage renders the local SVG, GIF, still images, and MP4 link. GitHub's Markdown renderer may handle embedded video controls differently from a local Markdown preview; the direct MP4 link is included as a fallback.
- Confirm the `v1.0.0` release contains all four artifacts and that the checksum manifest verifies after download.
- Confirm the repository visibility, branch protection, issue settings, and security reporting options match your intended community policy.
- Do not enable or advertise hosted AI analysis until the provider and model have been tested with non-sensitive sample data and their retention/region policies reviewed.

## What the repository owner must supply

The owner must create the repository, choose its visibility and namespace, authenticate Git, push the first commit, inspect GitHub Actions, and publish the release. Those actions require access to the owner's GitHub account and cannot be completed by this local packaging environment.
