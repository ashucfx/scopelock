# Pre-commit Hooks

Prevent unjustified capability over-reach from ever being committed to your repository.

## Option 1: ScopeLock Native Hook

```bash
scopelock init-hooks
```

This installs a shell script at `.git/hooks/pre-commit` that runs `scopelock scan-project .` before every commit.

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
        entry: scopelock scan-project
        args: ["."]
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

Now every `git commit` runs ScopeLock automatically.

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
| Windows (PowerShell) | ⚠️ Partial | ✅ Recommended |

!!! tip "Windows users"
    Use the **pre-commit framework** approach on Windows for the most reliable experience.
