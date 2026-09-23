# 🛡️ ScopeLock

> **"Never let AI code do more than you asked for."**  
> *Zero-Trust Security & Capability-Divergence Gate for AI-Generated Software*

[![CI Status](https://img.shields.io/badge/CI%2FCD-Passing-brightgreen?style=flat-square)]()
[![Benchmark Accuracy](https://img.shields.io/badge/Benchmark_Accuracy-100%25-blue?style=flat-square)]()
[![Average Latency](https://img.shields.io/badge/AST_Latency-%3C1ms-success?style=flat-square)]()
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
* **ScopeLock:** Bridges the semantic intent gap. It evaluates whether an API invocation is **justified by the user's declared prompt**. In an offline calculator, network egress is an **unjustified capability divergence** and is blocked immediately.

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
│  (FastAPI + Dark-Mode UI)    │                 │    (SARIF Export / PR Blocker)    │
└──────────────────────────────┘                 └───────────────────────────────────┘
```

---

## 3. Quickstart

### Installation
```bash
# Clone the repository
git clone https://github.com/ripplenexus/scopelock.git
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

# 4. Run the 25-program empirical benchmark suite
scopelock benchmark
```

### Launch Interactive Web Dashboard
```bash
scopelock serve --port 8000
# Open http://127.0.0.1:8000 in your browser
```

---

## 4. Empirical Benchmark Results (Research Paper Dataset)

Evaluated across **25 representative programs** (11 clean baselines, 14 capability-injected programs):

| Metric | Measured Value | Standard SAST / Linter Baseline |
| :--- | :--- | :--- |
| **Total Test Scenarios** | **25 Programs** | 25 Programs |
| **True Positives (Injected Over-reach Caught)** | **14 / 14 (100%)** | 0 / 14 (Missed by linters) |
| **False Positives (False Alarms on Clean Code)** | **0 (Zero)** | N/A |
| **Precision** | **100.00%** | N/A |
| **Recall (Sensitivity)** | **100.00%** | 0.00% |
| **F1-Score** | **100.00%** | 0.00% |
| **Average Execution Latency** | **0.66 ms / program** | 120 ms (ESLint / Sonar) |

---

## 5. Viva Voce & Academic Defense Guide

### Q1: Why not just use ESLint or SonarQube?
> **Answer:** Linters detect syntactic syntax errors and known CVE anti-patterns. They have no concept of what the software was intended to do. If a calculator connects to an external IP, ESLint reports zero errors because `fetch()` is valid syntax. ScopeLock evaluates whether an API invocation is *authorized* by the natural-language prompt.

### Q2: Why use an Abstract Syntax Tree (AST) instead of Regular Expressions?
> **Answer:** Regular expressions treat code as unstructured text and suffer from massive false positives (triggering on comments like `// TODO: fetch data` or variables like `let fetch = 5;`). Tree-sitter understands the formal language grammar and only inspects executable `call_expression` nodes.

### Q3: Is untrusted code executed on the host machine?
> **Answer:** No. ScopeLock operates primarily via deterministic static AST traversal. Source code is parsed without execution, ensuring host security is never compromised.

---

## Authors & Academic Citation
* **Ashutosh Shukla** (Roll No: 2300970100069)
* **Ayush Narayan Gupta** (Roll No: 2300970100074)
* **Ayush Kumar** (Roll No: 2300970100073)
* **Ankit Mishra** (Roll No: 2300970100047)

*Department of Computer Science and Engineering*  
*Galgotias College of Engineering & Technology, Greater Noida, UP, India*  
*Affiliated to Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow*
