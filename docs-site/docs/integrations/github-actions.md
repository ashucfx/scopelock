# GitHub Actions Integration

Integrate ScopeLock into your GitHub CI/CD pipeline to automatically block pull requests that introduce unjustified capability over-reach.

## Quick Setup

Add this to your workflow file:

```yaml title=".github/workflows/scopelock.yml"
name: ScopeLock Capability Audit

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  scopelock-audit:
    name: Zero-Trust Capability Gate
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install ScopeLock
        run: pip install scopelock

      - name: Run Capability Audit
        run: scopelock scan-project ./src
        # Exit code 1 automatically fails the job → blocks the PR
```

---

## Full Enterprise Setup (with SARIF)

This workflow audits your code **and** uploads results to GitHub's Security tab:

```yaml title=".github/workflows/scopelock-enterprise.yml"
name: ScopeLock Enterprise Audit

on:
  push:
    branches: [main]
  pull_request:

jobs:
  capability-audit:
    name: Capability Divergence Gate
    runs-on: ubuntu-latest
    permissions:
      security-events: write   # Required for SARIF upload
      contents: read

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install ScopeLock
        run: pip install scopelock

      - name: Run Audit (Terminal Output)
        run: scopelock scan-project ./src

      - name: Generate SARIF Report
        if: always()   # Run even if previous step failed
        run: |
          scopelock scan app.js \
            --prompt "$(cat .scopelock-intent.txt)" \
            --sarif > scopelock.sarif

      - name: Upload to GitHub Security Tab
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: scopelock.sarif
          category: scopelock
```

After setup, violations appear in:  
**GitHub Repo → Security → Code scanning alerts**

---

## Scan Only Changed Files (PR-Optimized)

For large repositories, scan only files changed in the PR:

```yaml
      - name: Get changed files
        id: changed
        uses: tj-actions/changed-files@v44
        with:
          files: |
            **/*.js
            **/*.ts
            **/*.py

      - name: Audit changed files
        if: steps.changed.outputs.any_changed == 'true'
        run: |
          for file in ${{ steps.changed.outputs.all_changed_files }}; do
            scopelock scan "$file" --prompt "$(git log -1 --pretty=%B)" --sarif >> results.sarif
          done
```

---

## LLM-Enhanced Mode (with OpenAI)

Enable richer intent decomposition using GPT-4o-mini:

```yaml
      - name: Install ScopeLock with LLM support
        run: pip install scopelock openai

      - name: Run Audit (LLM-enhanced)
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: scopelock scan-project ./src
```

Add `OPENAI_API_KEY` to your repository secrets under  
**Settings → Secrets and variables → Actions → New repository secret**

---

## Existing `scopelock_ci.yml`

Your repo already has a CI workflow at [`.github/workflows/scopelock_ci.yml`](https://github.com/ashucfx/scopelock/blob/main/.github/workflows/scopelock_ci.yml) that:

- Lints with `ruff`
- Runs all `pytest` tests
- Executes the 25-program benchmark
- Runs a self-audit on a clean snippet

---

## Badge for Your README

Add the CI status badge to your README:

```markdown
[![ScopeLock Audit](https://github.com/ashucfx/scopelock/actions/workflows/scopelock_ci.yml/badge.svg)](https://github.com/ashucfx/scopelock/actions/workflows/scopelock_ci.yml)
```

Result: [![ScopeLock Audit](https://img.shields.io/badge/ScopeLock-Passing-brightgreen)](https://github.com/ashucfx/scopelock)

---

## Troubleshooting

### Job fails on a clean codebase

This usually means a file is missing an `@intent:` annotation and the inferred intent is too broad. Add explicit annotations:

```javascript
// @intent: Pure utility functions — no network, filesystem, or process access
```

### SARIF upload fails

Ensure the job has `permissions: security-events: write` set.

### Slow scans on large repos

Use the [diff-aware approach](#scan-only-changed-files-pr-optimized) above.
