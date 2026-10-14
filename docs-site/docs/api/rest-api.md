# REST API Reference

The `scopelock serve` command exposes a REST API alongside the web dashboard. This allows programmatic integration from any language or toolchain.

## Base URL

```
http://127.0.0.1:8000
```

Start the server:

```bash
scopelock serve --port 8000
```

---

## Endpoints

### `GET /health`

Health check endpoint.

**Response:**
```json
{"status": "ok", "version": "1.0.0"}
```

---

### `POST /api/audit`

Audit a code snippet against a developer prompt.

**Request Body:**

```json
{
  "code": "string",      // Source code to audit (required)
  "prompt": "string",    // Developer intent prompt (required)
  "lang": "js"           // Language: js, ts, py, or python (optional, default: "js")
}
```

**Example:**

```bash
curl -X POST http://127.0.0.1:8000/api/audit \
  -H "Content-Type: application/json" \
  -d '{
    "code": "fetch(\"https://evil.com\")",
    "prompt": "Build a local offline calculator",
    "lang": "js"
  }'
```

**Response:**

```json
{
  "target_file": "snippet.js",
  "user_prompt": "Build a local offline calculator",
  "final_verdict": "FAILED",
  "total_violations": 1,
  "analysis_latency_ms": 0.66,
  "engine_version": "1.0.0",
  "timestamp": "2026-10-04T12:34:56.789Z",
  "policy": {
    "application_name": "Arithmetic Calculator CLI",
    "stated_intent": "Build a local offline calculator",
    "allowed_categories": [],
    "disallowed_categories": ["NETWORK", "FILESYSTEM", "PROCESS", "SECRET", "RUNTIME"]
  },
  "findings": [
    {
      "verdict": "UNJUSTIFIED",
      "risk_score": 0.95,
      "finding": "Unjustified NETWORK capability detected.",
      "recommendation": "Remove or refactor 'fetch' at Line 1, Column 0.",
      "observed": {
        "category": "NETWORK",
        "action": "NET_REQUEST",
        "raw_call": "fetch",
        "source_location": {
          "file": "snippet.js",
          "line": 1,
          "col": 0
        }
      }
    }
  ]
}
```

---

### `POST /api/intent`

Decompose a natural language prompt into a `ScopePolicy` without scanning code.

**Request Body:**

```json
{
  "prompt": "string"
}
```

**Example:**

```bash
curl -X POST http://127.0.0.1:8000/api/intent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Read local CSV file and compute statistics"}'
```

**Response:**

```json
{
  "application_name": "File Reader Utility",
  "stated_intent": "Read local CSV file and compute statistics",
  "allowed_categories": ["FILESYSTEM"],
  "disallowed_categories": ["NETWORK", "PROCESS", "SECRET", "RUNTIME"],
  "is_ambiguous": false
}
```

---

### `POST /api/audit/pdf`

Generate a PDF audit report for a code snippet.

**Request Body:** Same as `/api/audit`

**Response:** Binary PDF file (`Content-Type: application/pdf`)

**Example:**

```bash
curl -X POST http://127.0.0.1:8000/api/pdf \
  -H "Content-Type: application/json" \
  -d '{"code": "fetch(\"https://evil.com\")", "prompt": "Local calculator"}' \
  --output audit-report.pdf
```

The legacy `/api/pdf` path remains available as a compatibility alias.

### `POST /api/audit/sarif`

Return the audit as SARIF 2.1.0 JSON for CI integrations.

**Response:** SARIF JSON (`Content-Type: application/sarif+json`)

---

### `GET /api/benchmark`

Run the 25-program empirical benchmark suite and return results.

**Response:**

```json
{
  "total": 25,
  "passed": 25,
  "failed": 0,
  "precision": 1.0,
  "recall": 1.0,
  "f1_score": 1.0,
  "avg_latency_ms": 0.66,
  "results": [...]
}
```

---

## Error Responses

| HTTP Code | Meaning |
|---|---|
| `422` | Validation error — missing required field |
| `500` | Internal server error |

```json
{
  "detail": "Language 'ruby' is not supported. Use 'js' or 'py'."
}
```

---

## Interactive API Docs

The FastAPI server automatically generates interactive Swagger documentation:

- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI JSON:** [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)
