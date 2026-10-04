# `scopelock init-hooks`

Install an **automated Git pre-commit security hook** that runs ScopeLock before every `git commit`, preventing capability over-reach from being committed to the repository.

## Synopsis

```bash
scopelock init-hooks
```

!!! note "Requirements"
    This command must be run from the **root of a Git repository** (directory containing `.git/`).

## What It Does

Creates a `pre-commit` hook script at `.git/hooks/pre-commit` that:

1. Runs `scopelock scan-project .` before every commit
2. Blocks the commit if any unjustified capabilities are detected
3. Shows exactly which files and lines caused the violation

## Usage

```bash
# In your Git repository root:
scopelock init-hooks
```

```
[OK] ScopeLock Git pre-commit hook installed in .git/hooks/pre-commit!
Every 'git commit' will now automatically verify code against least privilege.
```

Now try to commit a file with a violation:

```bash
git add app.js
git commit -m "Add calculator"

# Output:
[ScopeLock] Running Zero-Trust Capability Audit...
[FAIL] app.js — NETWORK.fetch detected (unjustified)
[ScopeLock] Commit rejected: Unjustified capabilities detected.
```

The commit is **blocked** automatically.

## Manual Bypass (Emergency Only)

```bash
git commit --no-verify -m "Emergency fix"
```

!!! warning "Use `--no-verify` sparingly"
    Bypassing the hook defeats the purpose of zero-trust enforcement. Only use for genuine emergencies and follow up with a manual audit.

## Remove the Hook

```bash
rm .git/hooks/pre-commit
```

## Alternative: pre-commit Framework

For teams using the [pre-commit framework](https://pre-commit.com/), add ScopeLock to `.pre-commit-config.yaml`:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: scopelock
        name: ScopeLock Capability Audit
        entry: scopelock scan-project
        args: ["."]
        language: python
        pass_filenames: false
        always_run: true
```

Install with:
```bash
pre-commit install
```
