# `scopelock scan-project`

Recursively audit supported source files beneath a project directory. ScopeLock reads source files locally, extracts intent comments when present, and reports recognized capability calls against the selected policy.

## Synopsis

```bash
scopelock scan-project [DIRECTORY] [OPTIONS]
```

## Arguments

| Argument | Default | Description |
|---|---|---|
| `DIRECTORY` | `.` (current dir) | Path to the project root directory to audit |

## Options

| Option | Description |
|---|---|
| `--policy FILE` | Path to a `scopelock.json` configuration policy file |
| `--pdf FILE` | Optional path to save a PDF summary audit report |
| `--json` | Emit the complete aggregate project report as JSON |
| `--sarif` | Emit all project findings as SARIF 2.1.0 |

When either machine-readable option is selected, stdout contains only the JSON or SARIF document. The command exits with status `0` only when the audit passes; failed, review-needed or incomplete scans exit with status `1` so CI jobs can fail closed.

## Supported File Types

ScopeLock scans files with these extensions:

| Extension | Language |
|---|---|
| `.js`, `.mjs`, `.cjs` | JavaScript |
| `.jsx` | React JavaScript |
| `.ts` | TypeScript |
| `.tsx` | React TypeScript |
| `.py` | Python |

## Excluded directories

The following directories are automatically excluded:

```
node_modules/, .git/, .venv/, venv/, __pycache__/, dist/, build/, .next/
```

## Examples

### Scan current directory

```bash
scopelock scan-project .
```

### Scan a specific path

```bash
scopelock scan-project ./src
```

### Scan with a policy file

```bash
scopelock scan-project ./src --policy scopelock.json
```

### Scan and export PDF report

```bash
scopelock scan-project ./src --pdf audit-report.pdf
```

## In-Code Intent Annotations

ScopeLock checks the first 25 lines of each source file for an `@intent:` comment. The annotation can be a `//`, `/* ... */`, `#` or triple-quoted comment:

=== "JavaScript / TypeScript"

    ```javascript
    // @intent: REST API endpoint for user authentication — requires network and database
    async function loginUser(req, res) {
        // ...
    }
    ```

=== "Python"

    ```python
    # @intent: Parse local CSV file and compute statistical averages — no network access
    import csv, statistics

    def compute_averages(filepath: str) -> dict:
        # ...
    ```

For each file, the selected intent follows this precedence:

1. An `@intent:` comment in the source header.
2. The `intent` value for that relative path in `scopelock.json`.
3. A filename-based fallback, such as `user_auth.js` → `"Module for user auth"`.

Use an explicit annotation or policy entry when a filename does not accurately describe the module. The heuristic intent parser uses keywords, so vague descriptions can produce a policy that needs review.

## Sample Output

```
======================================================================
              SCOPELOCK: PROJECT REPOSITORY AUDIT SUMMARY
======================================================================
Total Files Scanned : 24
Compliant Files     : 22
Over-privileged     : 2
Total Violations    : 3
Total AST Latency   : 15.84 ms
----------------------------------------------------------------------
[PASS] src/utils/math.js                     (Local arithmetic calcul..)
[PASS] src/utils/formatter.js                (Format markdown headings..)
[FAIL] src/api/tracker.js                    (Log user activity locally..)
    * L4: NETWORK -> fetch (Unjustified NETWORK capability detected)
[FAIL] src/helpers/env_reader.js             (Read config values from..)
    * L2: SECRET -> process.env.DATABASE_URL (Suspicious SECRET access)
======================================================================

[AUDIT FAILED] Capability over-reach detected. Deployment blocked.

Exit code: 1
```

## Policy File (`scopelock.json`)

You can define per-module intent policies in a `scopelock.json` file:

```json
{
  "version": "1.0",
  "modules": {
    "src/api/weather.js": {
      "intent": "Fetch weather data from OpenWeatherMap API for a given city"
    },
    "src/utils/math.js": {
      "intent": "Local arithmetic calculator — pure functions only"
    }
  }
}
```

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | All files passed — no violations detected |
| `1` | The audit failed or needs review, or the project could not be scanned completely |
