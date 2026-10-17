# `scopelock init-hooks`

Install a Git pre-commit hook that runs a project-wide ScopeLock scan before every `git commit`.

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
3. Prints the files and lines reported by the scan

!!! note "Project-wide scan"
    The hook scans supported files present in the working tree, not only staged paths. Unstaged or untracked source files may affect the result. The native hook is a POSIX shell script and is intended for Linux, macOS or WSL; on Windows PowerShell, use the [pre-commit framework](../integrations/pre-commit.md) instead.

## Usage

```bash
# In your Git repository root:
scopelock init-hooks
```

```
[OK] ScopeLock Git pre-commit hook installed in .git/hooks/pre-commit!
Every 'git commit' will now automatically verify code against least privilege.
```

If the project scan finds a blocking result, the commit is rejected. For example:

```bash
git add app.js
git commit -m "Add calculator"

# Example output:
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
