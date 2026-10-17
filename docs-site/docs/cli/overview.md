# CLI Reference Overview

ScopeLock provides a comprehensive command-line interface for auditing AI-generated code.

## Installation

```bash
pip install scopelock
```

## Global Options

| Flag | Description |
|---|---|
| `--version` | Show ScopeLock version and exit |
| `--help` | Show help message |

## Commands

| Command | Description |
|---|---|
| [`scan`](scan.md) | Scan a single source file against a developer intent prompt |
| [`scan-project`](scan-project.md) | Recursively audit an entire codebase directory |
| `scan-staged` | Audit supported source files from the Git index |
| [`audit-code`](audit-code.md) | Directly audit a raw code snippet (no file needed) |
| [`serve`](serve.md) | Launch the interactive web dashboard |
| [`benchmark`](benchmark.md) | Run the curated source fixture checks |
| [`init-hooks`](init-hooks.md) | Install Git pre-commit security hook |

---

## Quick Examples

```bash
# Scan a JavaScript file
scopelock scan app.js --prompt "Build a local offline calculator"

# Scan with JSON output for tooling
scopelock scan app.js --prompt "..." --json

# Scan with SARIF for GitHub Security tab
scopelock scan app.js --prompt "..." --sarif > results.sarif

# Audit a raw code snippet
scopelock audit-code --code "fetch('https://evil.com')" --prompt "Local math CLI"

# Recursively audit a project
scopelock scan-project ./src

# Audit staged source contents before a commit
scopelock scan-staged

# Launch web dashboard
scopelock serve --port 8000

# Install pre-commit hook
scopelock init-hooks

# Run benchmarks
scopelock benchmark
```

---

## Exit Codes

ScopeLock follows standard Unix exit code conventions for CI/CD integration:

| Exit Code | Meaning |
|---|---|
| `0` | Audit PASSED — all capabilities are justified |
| `1` | Audit FAILED or NEEDS REVIEW — violations or incomplete analysis |
| `2` | Invalid project policy or command configuration |

This means any CI/CD pipeline that checks exit codes will automatically block deployment when over-reach is detected.

```yaml
# GitHub Actions — automatic failure on violation
- run: scopelock scan-project ./src
  # Returns exit 1 → job fails → PR blocked
```
