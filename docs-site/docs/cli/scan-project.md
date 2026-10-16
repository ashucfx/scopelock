# `scopelock scan-project`

Recursively audit an **entire codebase directory**. Automatically extracts `// @intent:` comment annotations from source files.

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

When either machine-readable option is selected, stdout contains only the JSON or SARIF document. The command exits with status `0` only when the audit passes; failed or review-needed audits exit with status `1` so CI jobs can fail closed.

## Supported File Types

ScopeLock scans files with these extensions:

| Extension | Language |
|---|---|
| `.js`, `.mjs`, `.cjs` | JavaScript |
| `.jsx` | React JavaScript |
| `.ts` | TypeScript |
| `.tsx` | React TypeScript |
| `.py` | Python |

## Auto-Ignored Directories

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

ScopeLock automatically extracts intent from source file headers — no `--prompt` flag needed:

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

If no `@intent:` is found, ScopeLock infers intent from the filename (e.g., `user_auth.js` → `"Module for user auth"`).

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
