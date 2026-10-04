# Research Paper Abstract

## Intent2Capability: A Zero-Trust AST Analysis Framework for Detecting Semantic Over-Reach in AI-Synthesized Code

**Ashutosh Shukla, Ayush Narayan Gupta, Ayush Kumar, Ankit Mishra**  
*Galgotias College of Engineering and Technology, Greater Noida, India*

---

## Abstract

The proliferation of AI-powered code generation tools — including GitHub Copilot, Cursor, Devin, and Claude Code — introduces a novel and systematically underexplored security threat: **semantic capability over-reach**. While these systems synthesize functionally correct software, they frequently acquire execution authority substantially exceeding the scope declared in the developer's natural-language requirement.

Traditional static analysis tools (ESLint, SonarQube, CodeQL) inspect code for syntactic correctness and known vulnerability patterns, operating without any concept of developer intent. Consequently, a `fetch()` call injected into an offline arithmetic calculator remains invisible to all existing SAST tools, as it is syntactically valid and matches no known CVE pattern.

This paper presents **ScopeLock**, a zero-trust capability-divergence gate that formalizes the **Semantic Intent Gap** as a set-theoretic operation:

```
Δ = C_obs \ C_exp
```

Where `C_obs` represents capabilities **observed** via deterministic Tree-sitter Abstract Syntax Tree analysis, and `C_exp` represents capabilities **expected** from developer intent decomposed through a deterministic heuristic engine with optional LLM augmentation. Any non-empty divergence set `Δ` constitutes a policy violation.

---

## Key Contributions

1. **Formal Capability-Intent Gap Model** — First formalization of the disconnect between natural-language prompts and AI-synthesized code authority
2. **Zero-Trust Policy Engine** — Deterministic, offline-capable intent decomposer producing formal `ScopePolicy` contracts
3. **Sub-Millisecond AST Analysis** — Tree-sitter-based scanner completing in 0.66ms per program (180× faster than ESLint)
4. **100% F1-Score on 25-Program Benchmark** — Zero false positives on clean code, zero false negatives on injected over-reach
5. **OASIS SARIF Output** — First intent-aware tool producing standards-compliant CI/CD security gate output

---

## System Overview

The ScopeLock pipeline consists of four stages:

1. **Intent Decomposition** — Natural language → `ScopePolicy` (heuristic + optional LLM)
2. **AST Scanning** — Source code → `ObservedCapability[]` (Tree-sitter)
3. **Alignment** — `Δ = C_obs \ C_exp` (zero-trust set difference)
4. **Reporting** — Terminal / JSON / SARIF / PDF output

---

## Benchmark Summary

| Metric | ScopeLock | ESLint | SonarQube |
|---|---|---|---|
| True Positives | **14/14 (100%)** | 0/14 (0%) | 0/14 (0%) |
| False Positives | **0** | N/A | N/A |
| F1-Score | **100%** | 0% | 0% |
| Avg. Latency | **0.66ms** | 45ms | 120ms |

---

## Citation

```bibtex
@article{shukla2026scopelock,
  title     = {Intent2Capability: A Zero-Trust AST Analysis Framework for 
               Detecting Semantic Over-Reach in AI-Synthesized Code},
  author    = {Shukla, Ashutosh and Gupta, Ayush Narayan and Kumar, Ayush 
               and Mishra, Ankit},
  journal   = {GCET Major Project Technical Report},
  year      = {2026},
  url       = {https://github.com/ashucfx/scopelock}
}
```
