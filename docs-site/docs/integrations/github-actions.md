# GitHub Actions Integration

Run ScopeLock from GitHub Actions to check changes for recognized capability use that falls outside the declared intent.

!!! note "A failed workflow does not automatically block merging"
    The example exits with a non-zero status when a scan fails. To require that result before merging, configure branch protection or a repository ruleset and mark the ScopeLock check as required. Without that repository setting, GitHub can still allow a pull request to merge.

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
        # Exit code 1 fails the job. Make this check required in branch rules to block merging.
```

---

## Full Enterprise Setup (with SARIF)

This workflow audits your code **and** uploads results to GitHub's Security tab. The repository needs the `security-events: write` permission for the upload step.

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
          scopelock scan-project ./src --sarif > scopelock.sarif

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

## Optional OpenAI intent decomposition

The default intent engine is local. To use the optional OpenAI integration, install the client and configure a repository secret:

```yaml
      - name: Install ScopeLock with OpenAI support
        run: pip install scopelock openai

      - name: Run Audit with remote intent decomposition
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: scopelock scan-project ./src
```

Add `OPENAI_API_KEY` to your repository secrets under  
**Settings → Secrets and variables → Actions → New repository secret**

When this integration is enabled, ScopeLock sends intent text to the OpenAI API for policy decomposition. It scans source files in the runner and does not include file contents in that request. See [Data handling](../concepts/security-model.md#data-handling).

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
