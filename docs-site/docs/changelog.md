# Changelog

All notable changes to ScopeLock are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-10-01

### 🚀 Initial Release

#### Added
- **Core AST Scanner** — Tree-sitter-based JavaScript and Python static analysis
- **Intent Decomposer Engine** — Deterministic heuristic + GPT-4o-mini fallback
- **Zero-Trust Aligner** — Set-theoretic capability divergence computation (Δ = C_obs \ C_exp)
- **CLI** — `scan`, `scan-project`, `audit-code`, `serve`, `benchmark`, `init-hooks` commands
- **Web Dashboard** — FastAPI + dark-mode interactive audit HUD
- **SARIF Output** — OASIS SARIF 2.1.0 compatible export for CI/CD integration
- **PDF Reports** — Professional PDF audit report generation
- **25-Program Benchmark** — Empirical evaluation dataset achieving 100% F1-Score
- **Git Pre-commit Hook** — `scopelock init-hooks` for automated enforcement
- **In-Code Annotations** — `// @intent:` and `# @intent:` comment support
- **Project Scanner** — Recursive repository auditing with `scopelock.json` policy support
- **GitHub Actions CI** — Automated lint, test, and benchmark pipeline

#### Capability Categories
- `NETWORK` — HTTP, WebSocket, socket connections
- `FILESYSTEM` — File read, write, delete operations
- `PROCESS` — Shell execution, child process spawning
- `SECRET` — Environment variable and credential access
- `DATABASE` — Database connections and queries
- `RUNTIME` — Dynamic eval and import

#### Supported Languages
- JavaScript (`.js`, `.mjs`, `.cjs`)
- TypeScript (`.ts`, `.tsx`)
- JSX (`.jsx`)
- Python (`.py`)

#### Research
- Accepted for GCET Major Project 2026
- 100% Precision, 100% Recall, 100% F1-Score on 25-program benchmark
- 0.66ms average analysis latency (180× faster than ESLint)

---

## [Upcoming]

See the comprehensive [Engineering Roadmap](roadmap.md) for architectural designs, component specifications, and delivery horizons.

### Planned for v1.1.0
- [ ] Documentation website (GitHub Pages)
- [ ] PyPI publication
- [ ] GitHub Actions Marketplace action
- [ ] Java language support
- [ ] Go language support
- [ ] Audit history persistence (SQLite)
- [ ] Diff-aware scanning (`scopelock scan-diff`)
- [ ] `--explain` LLM mode

### Planned for v1.2.0
- [ ] VS Code Extension
- [ ] npm package wrapper
- [ ] TypeScript-specific AST visitor
- [ ] Full SARIF v2.1 compliance (threadFlows, fixes)
- [ ] SBOM (Capability Bill of Materials) export
