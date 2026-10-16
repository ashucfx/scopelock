# 🛡️ ScopeLock

> **"Never let AI code do more than you asked for."**  
> *Zero-Trust Security & Capability-Divergence Gate for AI-Generated Software*

[![CI Status](https://github.com/ashucfx/scopelock/actions/workflows/scopelock_ci.yml/badge.svg)](https://github.com/ashucfx/scopelock/actions/workflows/scopelock_ci.yml)
[![Python Support](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-informational?style=flat-square)]()
[![License](https://img.shields.io/badge/License-Apache_2.0-blue?style=flat-square)]()

---

## 1. Problem Statement: The Semantic Intent Gap

When software developers prompt AI coding assistants (GitHub Copilot, Cursor, Devin, Claude Code), the model frequently synthesizes functional code that quietly acquires execution authority far beyond what the user requested.

For example, a prompt to *"Build a local addition calculator"* may output code that performs basic arithmetic but quietly includes background telemetry:
```javascript
function calculateTotal(price, taxRate) {
  const subtotal = price * (1 + taxRate);
  // Unrequested telemetry exfiltration
  fetch("https://analytics.tracker.org/log?val=" + subtotal);
  return subtotal;
}
```

* **Traditional Linters (ESLint, SonarQube, CodeQL):** Inspect code for syntax bugs and known CVE patterns. They find **zero errors** because `fetch()` is syntactically valid and not inherently vulnerable.
* **ScopeLock:** Compares recognized source-level API uses with a policy inferred from the declared prompt. CLI and CI integrations report findings and return a non-zero status for failed or incomplete audits. Static analysis does not prevent runtime effects by itself.

---

## 2. System Architecture

```
                    ┌────────────────────────────────────────┐
                    │    Natural-Language Developer Prompt   │
                    │  "Build a local arithmetic calculator" │
                    └───────────────────┬────────────────────┘
                                        │
                                        ▼
                    ┌────────────────────────────────────────┐
                    │        Intent Decomposer Engine        │
                    │  (Deterministic Heuristic + LLM JSON)  │
                    └───────────────────┬────────────────────┘
                                        │
                       Expected Capability Contract (C_exp)
                       { FS: NONE, NET: NONE, PROC: NONE }
                                        │
      ┌─────────────────────────────────┴─────────────────────────────────┐
      ▼                                                                   ▼
┌──────────────────────────────┐                         ┌───────────────────────────────────┐
│     AI-Synthesized Code      │                         │       Tree-sitter AST Visitor     │
│   (JavaScript / Python)      │                         │     (Sub-millisecond traversal)   │
└──────────────┬───────────────┘                         └─────────────────┬─────────────────┘
               │                                                           │
               └───────────────────────┬───────────────────────────────────┘
                                       │
                                       ▼
                    ┌────────────────────────────────────────┐
                    │    Zero-Trust Divergence Engine        │
                    │         Δ = C_obs \ C_exp              │
                    │   [DETECTED: NET.fetch (Line 4)]       │
                    └───────────────────┬────────────────────┘
                                        │
              ┌─────────────────────────┴─────────────────────────┐
              ▼                                                   ▼
┌──────────────────────────────┐                 ┌───────────────────────────────────┐
│    Interactive Web HUD       │                 │       DevSecOps CI/CD Gate        │
│  (FastAPI + Dark-Mode UI)    │                 │    (SARIF Export / Exit Status)  │
└──────────────────────────────┘                 └───────────────────────────────────┘
```

---

## 3. Quickstart

### Installation
```bash
# Clone the repository
git clone https://github.com/ashucfx/scopelock.git
cd scopelock

# Install in production editable mode
pip install -e .
```

### Run Developer CLI
```bash
# 1. Audit a code file against an intent prompt
scopelock scan app.js --prompt "Build a local offline calculator"

# 2. Audit a raw code snippet directly
scopelock audit-code --code "fetch('https://evil.com')" --prompt "Local math CLI"

# 3. Export audit results in OASIS SARIF format for CI/CD
scopelock scan app.js --prompt "Local math CLI" --sarif

# 4. Run the curated fixture regression checks
scopelock benchmark
```

### Launch Interactive Web Dashboard
```bash
scopelock serve --port 8000
# Open http://127.0.0.1:8000 in your browser
```

---

## 4. Fixture-Suite Checks

The repository includes **25 curated source fixtures**: 11 labeled without unauthorized capabilities and 14 labeled with at least one. Run `scopelock benchmark` to check the current implementation against these fixtures.

The runner reports **program-level** classification: a fixture labeled with one or more violations is counted as detected if the audit reports any violation. It does not measure per-event precision or partial coverage. Its latency is AST parsing time only; it excludes intent decomposition and alignment. These hand-curated fixtures are a regression check, not an estimate of real-world detection performance. No comparisons against other analyzers have been measured by this project.

---

## 5. Enterprise Usage & Workflows

### Recursive Repository Audit
Audit an entire codebase in seconds:
```bash
scopelock scan-project ./src
```

### In-Code Intent Annotations
Declare intent directly inside source code comments without passing CLI flags:
```javascript
// @intent: Local mathematical calculator for pricing calculations
function calculateSubtotal(price, taxRate) {
    return price * (1 + taxRate);
}
```

### Automated Git Pre-Commit Hook
Prevent unrequested permissions from ever being committed:
```bash
scopelock init-hooks
```

---

## 6. License & Community

ScopeLock is open-source software licensed under the [Apache 2.0 License](LICENSE).
Built for software engineering teams and AI developers requiring zero-trust execution assurance.
