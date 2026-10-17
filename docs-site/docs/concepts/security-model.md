# Security model and limitations

ScopeLock is a **static capability auditor**. It inspects source text with language parsers, records API patterns from its capability rules, and compares those observations with an intent-derived policy. It can help reviewers find unexpected authority in a change; it does not enforce permissions at runtime.

## Analysis flow

1. **Choose an intent.** A single-file scan takes `--prompt`. A project scan uses a source comment, then a matching `scopelock.json` entry, then a filename-based fallback.
2. **Parse source.** Tree-sitter visitors inspect supported JavaScript, TypeScript and Python files.
3. **Record recognized calls.** The scanner maps known API patterns to capability categories and source locations.
4. **Compare with policy.** The aligner assigns a verdict and findings based on the declared intent and observed calls.
5. **Return a result.** CLI commands print a report or emit JSON/SARIF. CI can use the command's exit status as a gate.

See the [intent engine](intent-engine.md), [capability taxonomy](taxonomy.md) and [divergence scoring](divergence.md) for their details.

## Capability categories

| Category | Examples of tracked behavior |
|---|---|
| `FILESYSTEM` | File reads, writes and deletes |
| `NETWORK` | HTTP requests, fetch calls and sockets |
| `PROCESS` | Shell commands and process spawning |
| `DATABASE` | Database connections and queries |
| `SECRET` | Environment and credential access patterns |
| `RUNTIME` | Dynamic evaluation and imports |

The [taxonomy reference](taxonomy.md) lists the API patterns currently recognized for each language. A pattern being present in source does not prove that the call will execute or succeed at runtime.

## What a result means

- **Passed** means the scan completed and no blocking finding was reported under the selected policy and current rules.
- **Failed** means the report contains a blocking capability finding.
- **Needs review** means the scan could not establish a reliable result, for example because of parser or file-reading diagnostics.

A passing result is not a certification that the program is secure. It means only that this scan did not report a blocking issue in the source it analyzed. Keep ordinary code review, dependency checks, tests and runtime protections in place.

!!! warning "ScopeLock does not execute or contain code"
    The scanner does not run the target program, intercept system calls, enforce an operating-system sandbox or stop a program from accessing resources. Use operating-system permissions, containers or other runtime controls when enforcement is required.

## Supported source and analysis boundaries

Project scans currently include `.js`, `.jsx`, `.ts`, `.tsx`, `.mjs`, `.cjs` and `.py` files. The scanner recognizes a finite set of API patterns; indirect calls, aliases, generated code, reflection, unsupported libraries and behavior hidden behind dependencies may not be represented in the findings. Parser diagnostics can also require manual review.

For project scans, intent is selected in this order:

1. An `@intent:` comment found in the first 25 lines of the source file.
2. A matching module entry in the configured `scopelock.json` file.
3. An intent inferred from the file name.

Provide explicit intent when the filename does not describe the module's purpose. Review inferred policies before treating a project result as a release gate.

## Data handling

The default heuristic intent engine runs locally and makes no external API request. The optional OpenAI integration runs only when the OpenAI package is installed, `OPENAI_API_KEY` is set, and offline mode is not forced. In that path, ScopeLock sends the intent text to the OpenAI API for policy decomposition; source file contents are not included in that request. OpenAI account terms and data settings apply to that optional request.

The local dashboard and REST API bind to `127.0.0.1` by default. Binding to `0.0.0.0` can make the server reachable from other machines on the network. Use that option only on a network you trust and restrict access using your network controls.

## Reporting an issue

If a scan produces an incorrect or surprising result, include a minimal source example, the declared intent, language, ScopeLock version and the command used. Remove secrets and private source before sharing a report in a public issue. See [Contributing](../contributing.md) for the project workflow.
