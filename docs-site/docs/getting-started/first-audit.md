# Your First Audit — Step by Step

This guide walks through a complete audit workflow, explaining what ScopeLock does at each stage.

---

## The Scenario

You asked GitHub Copilot to build a **CSV file reader**. The AI returned the following code:

```python title="csv_reader.py"
# @intent: Read local CSV file and parse rows into a list of dicts
import csv
import requests  # 🚨 You never asked for this

def read_csv(filepath: str) -> list[dict]:
    # Unexpected: telemetry ping before reading
    requests.post("https://telemetry.ai-tool.com/usage", json={"file": filepath})
    
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        return list(reader)
```

Two things happened:
1. `open()` — **Justified**: you asked for a file reader
2. `requests.post()` — **Unjustified**: telemetry you never requested

---

## Running the Audit

Since the file has an `# @intent:` annotation, ScopeLock picks it up automatically:

```bash
scopelock scan csv_reader.py --prompt "Read local CSV file and parse rows into a list of dicts"
```

Or scan the whole project (auto-extracts `@intent` comments):

```bash
scopelock scan-project .
```

---

## Understanding the Output

```
╔══════════════════════════════════════════════════════════╗
║  SCOPELOCK AUDIT REPORT                                 ║
╠══════════════════════════════════════════════════════════╣
║  File:    csv_reader.py                                 ║
║  Intent:  Read local CSV file and parse rows            ║
║  Verdict: ❌ FAILED — 1 violation                       ║
╠══════════════════════════════════════════════════════════╣
║  Finding 1: JUSTIFIED                                   ║
║  Category:  FILESYSTEM (FS_READ)                        ║
║  Call:      open(filepath)  — Line 8                    ║
║  Justification: Prompt explicitly mentions file reading ║
╠══════════════════════════════════════════════════════════╣
║  Finding 2: UNJUSTIFIED ⚠️                              ║
║  Category:  NETWORK (NET_HTTP_POST)                     ║
║  Call:      requests.post() — Line 6                    ║
║  Risk:      0.95 / 1.0 (CRITICAL)                       ║
║  The intent does not authorize network access.          ║
╚══════════════════════════════════════════════════════════╝
```

### Reading the Verdict

| Symbol | Meaning |
|---|---|
| ✅ **JUSTIFIED** | Capability explicitly authorized by your prompt |
| ⚠️ **SUSPICIOUS** | Capability permitted but target scope exceeds what was declared |
| ❌ **UNJUSTIFIED** | Capability completely unauthorized — code over-reach detected |
| 🔄 **NEEDS_REVIEW** | Prompt was ambiguous; manual review required |

---

## Exporting Results

=== "JSON (for tooling)"

    ```bash
    scopelock scan csv_reader.py --prompt "Read CSV file" --json
    ```

    ```json
    {
      "target_file": "csv_reader.py",
      "final_verdict": "FAILED",
      "total_violations": 1,
      "findings": [
        {
          "verdict": "UNJUSTIFIED",
          "risk_score": 0.95,
          "observed": {
            "category": "NETWORK",
            "raw_call": "requests.post",
            "source_location": {"line": 6, "col": 4}
          }
        }
      ]
    }
    ```

=== "SARIF (for GitHub Security tab)"

    ```bash
    scopelock scan csv_reader.py --prompt "Read CSV file" --sarif > results.sarif
    ```

    Upload to GitHub:
    ```yaml
    - uses: github/codeql-action/upload-sarif@v3
      with:
        sarif_file: results.sarif
    ```

=== "PDF Report"

    ```bash
    scopelock scan-project . --pdf audit-report.pdf
    ```

---

## Using In-Code Annotations

Instead of passing `--prompt` every time, declare intent inside your source file:

=== "JavaScript"

    ```javascript
    // @intent: Local arithmetic calculator — no network or file access required
    function calculateTotal(price, tax) {
        return price * (1 + tax);
    }
    ```

=== "Python"

    ```python
    # @intent: Read local CSV file and parse rows into structured data
    import csv

    def read_csv(path):
        with open(path) as f:
            return list(csv.DictReader(f))
    ```

=== "TypeScript"

    ```typescript
    // @intent: Format markdown headings from raw text input
    export function formatHeading(text: string): string {
        return `# ${text.trim()}`;
    }
    ```

ScopeLock automatically picks these up when running `scopelock scan-project`.

---

!!! tip "Next Steps"
    - Set up [automated CI/CD blocking](../integrations/github-actions.md)
    - Install [Git pre-commit hooks](../integrations/pre-commit.md)
    - Explore the [Web Dashboard](../cli/serve.md)
