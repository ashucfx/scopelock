# SARIF Output

ScopeLock produces **OASIS SARIF 2.1.0**-compatible output for seamless integration with GitHub Security, Azure DevOps, and any SARIF-compatible toolchain.

## Generating SARIF

```bash
# Single file
scopelock scan app.js --prompt "Build a local calculator" --sarif > results.sarif

# Project-wide (planned)
scopelock scan-project ./src --sarif > project.sarif
```

## SARIF Structure

```json
{
  "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "ScopeLock",
          "semanticVersion": "1.0.0",
          "informationUri": "https://github.com/ashucfx/scopelock"
        }
      },
      "results": [
        {
          "ruleId": "SL001",
          "level": "error",
          "message": {
            "text": "Unjustified NETWORK capability: fetch() at line 4 is not authorized by the stated intent."
          },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": { "uri": "app.js" },
                "region": { "startLine": 4, "startColumn": 2 }
              }
            }
          ]
        }
      ]
    }
  ]
}
```

## Uploading to GitHub Security Tab

```yaml title=".github/workflows/scopelock.yml"
- name: Run ScopeLock audit
  run: scopelock scan app.js --prompt "Local calculator" --sarif > scopelock.sarif

- name: Upload SARIF to GitHub
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: scopelock.sarif
    category: scopelock-capability-audit
```

Results appear in **Security → Code scanning alerts** with line-level annotations on PRs.

## Severity Mapping

| ScopeLock Verdict | SARIF Level |
|---|---|
| `UNJUSTIFIED` | `error` |
| `SUSPICIOUS` | `warning` |
| `JUSTIFIED` | `note` |
| `AMBIGUOUS` | `warning` |
