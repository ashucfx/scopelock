# Engineering Roadmap

This document outlines the architectural roadmap, planned features, and delivery milestones for ScopeLock.

---

## Vision & Horizon

ScopeLock bridges the **semantic intent gap** in AI-assisted software development. While traditional SAST and linters verify syntactic validity and known vulnerability signatures, ScopeLock evaluates whether code execution authority matches the developer's declared task intent.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                               SCOPE LOCK HORIZON                                 │
├───────────────────────┬──────────────────────────┬───────────────────────────────┤
│ v1.0.0 (Released)     │ v1.1.0 (Current Target)  │ v1.2.0 & Beyond               │
├───────────────────────┼──────────────────────────┼───────────────────────────────┤
│ • Tree-sitter AST     │ • Diff-Aware Auditing    │ • VS Code Extension (LSP)     │
│   (Python/JS/TS)      │   (`scopelock scan-diff`)│ • Go & Java Visitors          │
│ • Heuristic & LLM     │ • Persistent SQLite      │ • Capability BOM (CBOM/SBOM)  │
│   Intent Engine       │   Audit History          │ • Intra-procedural Data-Flow  │
│ • Zero-Trust Aligner  │ • Remediation Guidance   │ • Rich SARIF ThreadFlows      │
│ • CLI, Web HUD, SARIF │   (`--explain` Mode)     │ • Enterprise Policy Hub       │
│ • PDF Reporting       │ • GitHub Marketplace     │ • Interactive Clarification   │
│ • Pre-commit Hook     │   Composite Action       │   Dialogue Engine             │
└───────────────────────┴──────────────────────────┴───────────────────────────────┘
```

---

## Release Milestones

| Milestone | Target | Focus Area | Status |
|:---|:---|:---|:---|
| **v1.0.0** | Current | Core AST engine, dual intent decomposer, aligner, CLI & Web HUD | Released |
| **v1.1.0** | Near Term | Developer workflow acceleration, incremental diff scanning, persistent history | In Planning |
| **v1.2.0** | Medium Term | Polyglot support (Go/Java), editor integration (VS Code), CBOM compliance | Planned |
| **v1.3.0** | Long Term | Data-flow target resolution, call alias tracking, enterprise policy syncing | Research |

---

## Detailed Specifications for Unbuilt Features

### 1. Diff-Aware Incremental Auditing (`scopelock scan-diff`)

* **Target Milestone:** v1.1.0  
* **Track:** Developer Experience & CI/CD Performance  
* **Problem Statement:**  
  Running full repository scans on large codebases in pre-commit hooks or PR checks creates unnecessary latency and reports legacy findings in unchanged files. Developers need immediate verification that *their incremental additions* do not introduce unrequested capabilities.

* **Architecture & Mechanics:**
  1. **Git Diff Inspection:** Execute `git diff` against a target baseline (`HEAD~1`, `--base origin/main`, or `--staged` index content).
  2. **Hunk Line Mapping:** Parse unified diff hunks into added line intervals `[line_start, line_end]` per file.
  3. **AST Node Filtering:** Run Tree-sitter parsing on the changed source; filter detected capability observations to only those whose AST node line spans intersect with added diff hunks.
  4. **Intent Contextualization:** Extract intent from file-level `@intent:` comments, `scopelock.json`, or an optional `--prompt` / PR description flag.
  5. **Divergence Evaluation:** Evaluate only newly introduced operations, failing closed if any added line introduces an unjustified capability.

* **CLI Interface:**
  ```bash
  # Audit only staged changes before commit
  scopelock scan-diff --staged

  # Audit changes relative to the default branch in CI
  scopelock scan-diff --base origin/main --sarif > diff-report.sarif
  ```

* **Acceptance Criteria:**
  - Capability invocations on unchanged lines are ignored.
  - Newly added capability invocations on modified lines are caught and reported.
  - Zero false positives on files with purely non-capability diffs (e.g., formatting/docstring changes).

---

### 2. Persistent Audit History & Metrics Engine (`scopelock history`)

* **Target Milestone:** v1.1.0  
* **Track:** Governance & Metrics  
* **Problem Statement:**  
  Security teams and engineering leads lack visibility into capability trends over time, recurring policy violations, and divergence frequency across repositories.

* **Architecture & Schema:**
  - **Storage:** Lightweight embedded SQLite database located at `.scopelock/history.db` (auto-created on first audit run).
  - **Schema:**
    ```sql
    CREATE TABLE audit_runs (
        run_id TEXT PRIMARY KEY,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        trigger TEXT,              -- 'cli', 'pre-commit', 'github-actions', 'web-hud'
        commit_hash TEXT,
        branch TEXT,
        files_scanned INTEGER,
        violations_count INTEGER,
        verdict TEXT,              -- 'PASSED', 'FAILED', 'NEEDS_REVIEW'
        duration_ms REAL
    );

    CREATE TABLE audit_findings (
        finding_id TEXT PRIMARY KEY,
        run_id TEXT REFERENCES audit_runs(run_id),
        file_path TEXT,
        category TEXT,             -- 'NETWORK', 'FILESYSTEM', 'PROCESS', etc.
        action TEXT,
        target TEXT,
        line_number INTEGER,
        risk_score REAL,
        verdict TEXT
    );
    ```

* **CLI Interface:**
  ```bash
  # View recent audit history
  scopelock history list --limit 10

  # Inspect a specific historical run
  scopelock history show <run-id>

  # Export aggregated metrics to JSON or CSV
  scopelock history stats --days 30 --format json
  ```

---

### 3. Contextual LLM Remediation Guidance (`--explain`)

* **Target Milestone:** v1.1.0  
* **Track:** Developer Usability  
* **Problem Statement:**  
  When an audit fails due to capability divergence, developers (especially those using AI code generators) often need actionable advice on how to replace the disallowed API with an authorized offline pattern, or how to refine their prompt.

* **Architecture & Mechanics:**
  - **Dual Mode Operation:**
    1. **Offline Rule-Based Explainer:** Fast, deterministic advice lookup for common patterns (e.g., replacing `fetch()` in offline calculation with local parameter passing; replacing `child_process.exec()` with native language libraries).
    2. **LLM Remediation Synthesizer (Optional):** When `OPENAI_API_KEY` is present and `--explain` is passed, sends the finding metadata, source snippet, and declared intent to generate minimal code diff suggestions.
  - **Privacy Guarantee:** Privacy filters redact local filesystem paths, environment variable values, and inline credentials before sending prompts to external APIs.

---

### 4. Official GitHub Actions Marketplace Action (`action.yml`)

* **Target Milestone:** v1.1.0  
* **Track:** DevSecOps Integrations  
* **Problem Statement:**  
  Users currently configure multi-step shell scripts in GitHub Actions. A dedicated marketplace action streamlines deployment into a single YAML block with automatic SARIF upload and PR status checks.

* **Sample Usage:**
  ```yaml
  - name: ScopeLock Capability Audit
    uses: ashucfx/scopelock@v1
    with:
      path: "./src"
      mode: "diff"
      fail-on-divergence: "true"
      sarif-output: "scopelock-results.sarif"
  ```

---

### 5. VS Code Interactive Extension (Language Server Protocol)

* **Target Milestone:** v1.2.0  
* **Track:** IDE & Real-Time Security  
* **Problem Statement:**  
  Catching capability divergence during CI/CD or pre-commit requires context switching. Developers need feedback directly in the editor as code is typed or generated by GitHub Copilot / Cursor.

* **Architecture:**
  - TypeScript-based VS Code extension communicating with ScopeLock via CLI daemon or WebAssembly-compiled AST engine.
  - **Core Features:**
    1. **Inline Diagnostics:** Red squiggles under calls not justified by the file's `@intent:` header.
    2. **Hover Tooltip:** Detailed capability classification, risk score, and justification status.
    3. **Code Actions (Quick Fixes):** One-click options to "Remove unauthorized call" or "Add capability to @intent annotation".
    4. **Activity Bar Panel:** Tree view of detected capabilities across the active file, categorized by status (Authorized, Unjustified, Suspicious).
    5. **Intent Autocomplete:** Contextual completion for `@intent:` comments based on file structure.

---

### 6. Polyglot Visitor Expansion: Go & Java

* **Target Milestone:** v1.2.0  
* **Track:** Language Support  
* **Grammar & Mapping Matrix:**
  | Language | Parser | Key Mapped Libraries & APIs |
  |:---|:---|:---|
  | **Go** | `tree-sitter-go` | `net/http`, `net`, `os`, `os/exec`, `database/sql`, `syscall`, `io/ioutil` |
  | **Java** | `tree-sitter-java` | `java.net.HttpURLConnection`, `java.net.http.HttpClient`, `java.lang.ProcessBuilder`, `Runtime.getRuntime().exec()`, `java.io.File`, `java.nio.file.Files`, `System.getenv()`, `java.sql.*` |

---

### 7. Capability Bill of Materials (CBOM / SBOM Export)

* **Target Milestone:** v1.2.0  
* **Track:** Compliance & Supply Chain Security  
* **Problem Statement:**  
  Enterprise governance and software supply chain standards (NIST SP 800-218, OWASP) require verifiable manifests of declared vs. observed software capabilities.
* **Format:** CycloneDX 1.6 and SPDX 3.0 compatible extensions via `scopelock scan-project . --cbom`.

---

### 8. Intra-Procedural Data-Flow Target Resolution

* **Target Milestone:** v1.3.0  
* **Track:** Analysis Depth  
* **Technical Design:**
  - Introduce local constant folding and intra-procedural string propagation within the Tree-sitter AST visitor.
  - Resolve simple variable assignments (`const endpoint = "https://safe.api.com"; fetch(endpoint);`).
  - Support glob-pattern policy targets in `scopelock.json` (e.g., `https://*.company.com/*`, `/tmp/app_*.tmp`).

---

## Academic & Research Deliverables (GCET Major Project VII)

As part of the academic evaluation and research rigor:
1. **Component-Independent Benchmarking:** Establish gold-labeled test datasets for intent decomposition and AST visitors independently, moving beyond synthetic smoke tests.
2. **Reproducible Measurement Protocols:** Standardize hardware/software reporting standards for AST parse latency and alignment throughput.
3. **Formal Negation & Conjunction Verification:** Formal verification of lexical and compositional intent policies against adversarial prompt variations.
