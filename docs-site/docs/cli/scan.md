# `scopelock scan`

Scan a **single source file** against a developer intent prompt.

## Synopsis

```bash
scopelock scan FILE_PATH --prompt PROMPT [OPTIONS]
```

## Arguments

| Argument | Required | Description |
|---|---|---|
| `FILE_PATH` | ✅ Yes | Path to the source file to audit (`.js`, `.ts`, `.py`, etc.) |

## Options

| Option | Short | Default | Description |
|---|---|---|---|
| `--prompt` | `-p` | *required* | Natural-language requirement prompt |
| `--json` | | `False` | Output structured JSON instead of terminal text |
| `--sarif` | | `False` | Output OASIS SARIF 2.1 format for CI/CD integration |

## Examples

### Basic scan

```bash
scopelock scan app.js --prompt "Build a local offline calculator"
```

### Scan a Python file

```bash
scopelock scan utils.py --prompt "Parse CSV file and return list of records"
```

### JSON output (for programmatic use)

```bash
scopelock scan app.js --prompt "Build a local calculator" --json
```

```json
{
  "target_file": "app.js",
  "user_prompt": "Build a local offline calculator",
  "final_verdict": "FAILED",
  "total_violations": 1,
  "analysis_latency_ms": 0.66,
  "findings": [
    {
      "verdict": "UNJUSTIFIED",
      "risk_score": 0.95,
      "finding": "Unjustified NETWORK capability detected.",
      "recommendation": "Remove fetch() at Line 4.",
      "observed": {
        "category": "NETWORK",
        "action": "NET_REQUEST",
        "raw_call": "fetch",
        "source_location": {
          "file": "app.js",
          "line": 4,
          "col": 2
        }
      }
    }
  ]
}
```

### SARIF output (for GitHub Security tab)

```bash
scopelock scan app.js --prompt "Build a local calculator" --sarif > results.sarif
```

Upload SARIF to GitHub in CI:

```yaml
- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: results.sarif
```

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Audit PASSED |
| `1` | Audit FAILED (violations found) |

## Output Format (Terminal)

The terminal output is color-coded for easy reading:

- 🟢 **Green** — Justified capabilities
- 🟡 **Yellow** — Suspicious (conditionally justified)
- 🔴 **Red** — Unjustified (policy violation)
