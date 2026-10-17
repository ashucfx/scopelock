# Installation

## Requirements

| Requirement | Version |
|---|---|
| Python | 3.10–3.13 |
| Operating System | Windows, macOS, Linux |
| Git | Any (for pre-commit hooks) |

Python 3.14 and newer are not currently declared as supported by the package. Use a supported Python interpreter when creating a virtual environment.

---

## Option 1: Install from PyPI (Recommended)

```bash
pip install scopelock
```

On Windows, if you do not want to activate a virtual environment, use its interpreter directly:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install scopelock
.\.venv\Scripts\scopelock.exe --version
```

Replace `3.13` with another installed supported version (`3.10`, `3.11` or `3.12`). If `py -3.13` reports that no runtime is installed, install that Python version first or use `py --list` to see available versions.

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

## Optional: Remote intent decomposition

ScopeLock uses local keyword rules by default and does not require an API key. To use the optional OpenAI intent decomposer, install the client package and set a key.

```bash
pip install openai
export OPENAI_API_KEY="sk-..."
```

In PowerShell, set the key for the current terminal session with:

```powershell
$env:OPENAI_API_KEY = "your-key"
```

When enabled, ScopeLock sends the requirement text to the OpenAI API for policy decomposition. Source files are scanned locally and are not sent in that request. If the optional client or API call is unavailable, ScopeLock falls back to its local heuristic engine. See [Data handling](../concepts/security-model.md#data-handling) before enabling the integration.

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
