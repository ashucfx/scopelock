# VS Code Integration

> **🚧 Coming Soon** — The ScopeLock VS Code extension is under active development.

The extension will bring real-time capability auditing directly into your editor, with inline highlights the moment you save a file.

---

## Planned Features

<div class="grid cards" markdown>

-   :material-alert-circle-outline: **Inline Diagnostics**

    ---

    Red squiggles under unjustified API calls — just like ESLint.
    
    `fetch()` in a calculator? Highlighted instantly.

-   :material-eye: **Hover Tooltips**

    ---

    Hover over any flagged call to see:
    - Risk tier (UNJUSTIFIED / SUSPICIOUS)
    - Risk score
    - Recommendation

-   :material-sidebar-collapse: **Capability Sidebar**

    ---

    A dedicated panel showing all capabilities detected in the current file, color-coded by verdict.

-   :material-comment-check: **`@intent:` Autocomplete**

    ---

    Type `@intent:` and get smart suggestions based on your filename and imports.

</div>

---

## Preview (Planned UI)

```
src/calculator.js                                  🛡️ ScopeLock: ❌ 1 violation

  1  // @intent: Local offline arithmetic calculator
  2  
  3  function calculateTotal(price, taxRate) {
  4    const subtotal = price * (1 + taxRate);
  5    fetch("https://analytics.tracker.org/log?val=" + subtotal);
     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     ⚠️ UNJUSTIFIED NETWORK access — intent does not authorize egress
        Risk: 0.95 | Remove fetch() before deploying
  6    return subtotal;
  7  }
```

---

## Workaround (Until Extension is Released)

### Using the ScopeLock Web Dashboard

Launch the dashboard and use it as a side-by-side audit tool:

```bash
scopelock serve --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) alongside VS Code. Paste code into the dashboard to audit in real time.

### Using VS Code Tasks

Add ScopeLock as a VS Code task for one-click auditing:

```json title=".vscode/tasks.json"
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "ScopeLock: Audit Current File",
      "type": "shell",
      "command": "scopelock scan ${file} --prompt \"$(head -1 ${file} | sed 's|// @intent: ||')\"",
      "group": "test",
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      },
      "problemMatcher": []
    },
    {
      "label": "ScopeLock: Audit Project",
      "type": "shell",
      "command": "scopelock scan-project ${workspaceFolder}",
      "group": "test",
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      }
    }
  ]
}
```

Run via: **Terminal → Run Task → ScopeLock: Audit Project**

---

## Get Notified

Star the repository to get notified when the extension launches:  
[github.com/ashucfx/scopelock](https://github.com/ashucfx/scopelock)

!!! tip "Want to contribute?"
    The VS Code extension is a great contribution opportunity. See [Contributing](../contributing.md) to get involved.
