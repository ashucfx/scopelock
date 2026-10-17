# `scopelock init-hooks`

Install a Git pre-commit hook that runs a project-wide ScopeLock scan before every `git commit`.

## Synopsis

```bash
scopelock init-hooks
```

!!! note "Requirements"
    This command must be run from within a Git repository.

## What It Does

Creates a `pre-commit` hook script in Git's configured hooks directory that:

1. Runs `scopelock scan-staged` before every commit
2. Reads supported source files and contents from the Git index, not the working tree
3. Returns non-zero for violations, parser diagnostics, or incomplete scans
4. Leaves an existing pre-commit hook unchanged; add `scopelock scan-staged` to that hook manually

## Usage

```bash
# In your Git repository root:
scopelock init-hooks
```

```
[OK] ScopeLock Git pre-commit hook installed.
Each commit checks supported source files in the Git index.
```

If the project scan finds a blocking result, the commit is rejected. For example:

```bash
git add app.js
git commit -m "Add calculator"

# Output:
[ScopeLock] Auditing staged source files...
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

In PowerShell:

```powershell
Remove-Item .git/hooks/pre-commit
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
        entry: scopelock scan-staged
        language: python
        pass_filenames: false
        always_run: true
```

Install with:
```bash
pre-commit install
```
