# `scopelock serve`

Launch the **interactive ScopeLock DevSecOps Web Dashboard** — a real-time audit interface with live code scanning, pre-loaded demo scenarios, and PDF report generation.

## Synopsis

```bash
scopelock serve [OPTIONS]
```

## Options

| Option | Default | Description |
|---|---|---|
| `--host` | `127.0.0.1` | Binding host address |
| `--port` | `8000` | HTTP server port |

## Examples

### Launch locally (default)

```bash
scopelock serve
# Open: http://127.0.0.1:8000
```

### Custom port

```bash
scopelock serve --port 9090
```

### Expose on network (for team access)

```bash
scopelock serve --host 0.0.0.0 --port 8000
```

!!! warning "Security Note"
    Using `--host 0.0.0.0` exposes the dashboard to your network. Only do this on trusted private networks.

## Dashboard Features

The web dashboard provides:

- **Live Code Editor** — Write or paste code and see audit results in real time
- **Intent Prompt Field** — Declare your requirement in plain English
- **Pre-loaded Demo Scenarios** — 5 curated examples showcasing different violation types
- **Capability Visualization** — Color-coded breakdown of all detected capabilities
- **PDF Export** — One-click downloadable audit report
- **Benchmark Runner** — Execute the 25-program empirical benchmark suite
- **SARIF Export** — Download machine-readable SARIF 2.1 output

## REST API Endpoints

The `serve` command also exposes a REST API:

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Serve the web dashboard HTML |
| `POST` | `/api/audit` | Audit a code snippet |
| `POST` | `/api/intent` | Decompose a prompt into a policy |
| `GET` | `/api/benchmark` | Run and return benchmark results |
| `POST` | `/api/pdf` | Generate and download a PDF report |
| `GET` | `/health` | Health check endpoint |

### Example API call

```bash
curl -X POST http://127.0.0.1:8000/api/audit \
  -H "Content-Type: application/json" \
  -d '{
    "code": "fetch(\"https://analytics.tracker.org\")",
    "prompt": "Build a local offline calculator",
    "lang": "js"
  }'
```

See the full [REST API Reference](../api/rest-api.md) for complete documentation.
