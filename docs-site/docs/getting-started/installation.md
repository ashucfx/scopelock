# Installation

## Requirements

| Requirement | Version |
|---|---|
| Python | ≥ 3.10 |
| Operating System | Windows, macOS, Linux |
| Git | Any (for pre-commit hooks) |

---

## Option 1: Install from PyPI (Recommended)

```bash
pip install scopelock
```

Verify the installation:

```bash
scopelock --version
# scopelock v1.0.0
```

---

## Option 2: Install from Source

```bash
git clone https://github.com/ashucfx/scopelock.git
cd scopelock
pip install -e .
```

For development with all test dependencies:

```bash
pip install -e ".[dev]"
```

---

## Option 3: pipx (Isolated Install)

[pipx](https://pipx.pypa.io/) installs CLI tools in isolated environments:

```bash
pipx install scopelock
```

---

## Optional: LLM-Enhanced Intent Analysis

ScopeLock works **100% offline** by default. To enable GPT-4o-mini enhanced intent decomposition:

```bash
pip install openai
export OPENAI_API_KEY="sk-..."
```

When `OPENAI_API_KEY` is set, ScopeLock uses the LLM for richer intent parsing and automatically falls back to offline mode if the API is unavailable.

---

## Verify Installation

```bash
# Check version
scopelock --version

# Run a quick self-test
scopelock audit-code \
  --code "function add(a, b) { return a + b; }" \
  --prompt "Build a local addition calculator"

# Expected output: PASSED (no violations)
```

---

## Uninstall

```bash
pip uninstall scopelock
```

---

!!! tip "Next Step"
    Follow the [Quickstart Guide](quickstart.md) to run your first capability audit in under 2 minutes.
