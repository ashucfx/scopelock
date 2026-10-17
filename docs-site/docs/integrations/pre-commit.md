# Pre-commit Hooks

Run a ScopeLock project scan before a local commit is created.

!!! note "The hook scans the working tree"
    Both examples below run `scopelock scan-project .` over the repository files on disk; they do not limit the scan to staged paths. Fix, annotate or exclude any unrelated finding before committing, or run the check manually while preparing the change.

## Option 1: ScopeLock Native Hook

```bash
scopelock init-hooks
```

This installs a shell script in Git's configured hooks directory that runs `scopelock scan-staged` before every commit. It reads supported source contents from the Git index, leaving unstaged edits out of the scan. If a pre-commit hook already exists, it is preserved; add `scopelock scan-staged` to it manually.

See the [`init-hooks` command reference](../cli/init-hooks.md) for details.

---

## Option 2: pre-commit Framework (Recommended for Teams)

The [pre-commit](https://pre-commit.com/) framework manages hooks declaratively and makes it easy for the whole team to use the same hooks.

### Setup

```bash
pip install pre-commit
```

Add ScopeLock to your `.pre-commit-config.yaml`:

```yaml title=".pre-commit-config.yaml"
repos:
  # ... your existing hooks ...

  - repo: local
    hooks:
      - id: scopelock
        name: ScopeLock — Zero-Trust Capability Audit
        entry: scopelock scan-staged
        language: python
        additional_dependencies: [scopelock]
        pass_filenames: false
        always_run: true
        stages: [commit]
```

Install the hooks:

```bash
pre-commit install
```

Now every `git commit` runs a project-wide ScopeLock scan automatically.

### Test manually

```bash
pre-commit run scopelock --all-files
```

---

## How It Works

When you run `git commit`:

```
$ git commit -m "Add calculator feature"

[ScopeLock] Running Zero-Trust Capability Audit...

Scanning: src/calculator.js ............... ✅ PASS
Scanning: src/utils/formatter.js .......... ✅ PASS  
Scanning: src/api/tracker.js .............. ❌ FAIL
  L4: NETWORK → fetch() — Unjustified (risk: 0.95)

[ScopeLock] Commit REJECTED: Unjustified capabilities detected.
Fix the violations above, then re-commit.
```

The commit is **blocked**. Fix the violation, then try again.

---

## Cross-Platform Support

| Platform | `init-hooks` | pre-commit framework |
|---|---|---|
| Linux | ✅ | ✅ |
| macOS | ✅ | ✅ |
| Windows (WSL) | ✅ | ✅ |
| Windows (PowerShell) | ⚠️ Native hook uses a POSIX shell script | ✅ |

!!! tip "Windows users"
    Use the **pre-commit framework** approach on Windows for the most reliable experience.
