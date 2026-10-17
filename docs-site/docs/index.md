---
hide:
  - navigation
  - toc
---

<div class="hero-section" markdown>

<p class="hero-eyebrow">Local-first capability auditing</p>

# Make code scope explicit.

## ScopeLock compares the capabilities found in source code with the work a feature is meant to do.

<p class="hero-copy">Run it from the command line, add it to a pull request workflow, or use the local dashboard. Start with one file and grow into project-wide checks when you are ready.</p>

<div class="hero-buttons" markdown>

[Install ScopeLock](getting-started/installation.md){ .md-button .md-button--primary }
[Run your first audit](getting-started/quickstart.md){ .md-button }
[Explore the CLI](cli/overview.md){ .md-button }

</div>
</div>

## One clear path from intent to finding {.home-section-title}

<div class="grid cards" markdown>

-   **1. Describe the work**

    ---

    Provide a requirement with `--prompt`, or add an `@intent:` comment to a source file.

-   **2. Scan the source**

    ---

    ScopeLock parses supported JavaScript, TypeScript and Python files and records recognized capability calls.

-   **3. Review the difference**

    ---

    Read the terminal report, export JSON or SARIF, and decide whether each finding belongs in the change.

</div>

```bash
pip install scopelock
scopelock scan app.js --prompt "Build a local offline calculator"
```

## Pick up where you are {.home-section-title}

<div class="grid cards" markdown>

-   :material-rocket-launch-outline: **New to ScopeLock?**

    ---

    Install the package, run a small example, and learn how to read the result.

    [Start the quickstart →](getting-started/quickstart.md)

-   :material-console: **Working from a terminal?**

    ---

    Browse command syntax, options, output formats and exit codes.

    [Open the CLI reference →](cli/overview.md)

-   :material-source-pull: **Adding a CI check?**

    ---

    Configure a pull request gate and, optionally, upload SARIF findings.

    [Set up GitHub Actions →](integrations/github-actions.md)

-   :material-code-braces: **Integrating from code?**

    ---

    Use the Python SDK or call the local REST API.

    [Browse the API reference →](api/python-sdk.md)

</div>

## What ScopeLock checks {.home-section-title}

ScopeLock performs **static source analysis**. It looks for recognized APIs associated with filesystem, network, process, database, secret and runtime capabilities, then compares those observations with a policy derived from the declared intent.

| Question | Where to learn more |
|---|---|
| Which calls are recognized? | [Capability taxonomy](concepts/taxonomy.md) |
| How does text become a policy? | [Intent engine](concepts/intent-engine.md) |
| What do the verdicts and scores mean? | [Divergence scoring](concepts/divergence.md) |
| What are the scanner's limits? | [Security model and limitations](concepts/security-model.md) |

!!! warning "Static analysis is not a sandbox"
    ScopeLock reports recognized source-level capability use. It does not execute or contain code, and a clean result does not prove that a program is safe. Review important findings and use runtime controls appropriate to your application.

## Choose an integration {.home-section-title}

=== "GitHub Actions"

    Run project scans on pushes and pull requests. A non-zero audit exit code can fail the job.

    [Configure the workflow →](integrations/github-actions.md)

=== "Pre-commit"

    Catch findings before a local commit is created.

    [Install the hook →](integrations/pre-commit.md)

=== "Dashboard and REST API"

    Run the local web interface or send requests to the local API server.

    [Start the server →](cli/serve.md) · [Read the API docs →](api/rest-api.md)

## Documentation map {.home-section-title}

| Section | Covers |
|---|---|
| [Getting started](getting-started/installation.md) | Installation, quickstart and a complete first audit |
| [CLI reference](cli/overview.md) | Command options, machine-readable output and exit codes |
| [Concepts and security](concepts/intent-gap.md) | Intent, capabilities, verdicts, limitations and SARIF |
| [Integrations](integrations/github-actions.md) | GitHub Actions, pre-commit, VS Code and annotations |
| [API reference](api/python-sdk.md) | Python interfaces and local HTTP endpoints |
| [Benchmarks](benchmarks/benchmarks.md) | Included evaluation set, results and methodology |

## Offline by default {.home-section-title}

The default intent engine uses local keyword rules and needs no API key. If the optional OpenAI integration is installed and `OPENAI_API_KEY` is set, ScopeLock can send the **requirement text** to the configured model for policy decomposition. Source files are scanned locally and are not included in that request. See [data handling and limitations](concepts/security-model.md#data-handling).

## Benchmark scope {.home-section-title}

The repository includes a small, deterministic evaluation set for checking known examples. Its scores describe those cases only; they are not a guarantee of detection on arbitrary software. Read the [benchmark methodology and results](benchmarks/benchmarks.md) before interpreting the numbers.
