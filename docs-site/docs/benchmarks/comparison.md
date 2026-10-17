# How ScopeLock fits with other code checks

ScopeLock focuses on one review question: **does the source use capabilities that are outside the declared intent?** It is best used alongside tools that cover other risks.

## Different tools answer different questions

| Tool category | Typical question | How it complements ScopeLock |
|---|---|---|
| Formatter or linter | Does source follow formatting and configured code rules? | Use it for consistency and project-specific conventions. |
| Static application security testing (SAST) | Does source match known vulnerability patterns or data-flow rules? | Use it for security rules, taint paths and weaknesses covered by its rules. |
| Dependency scanner | Do installed packages have known vulnerabilities or policy issues? | Use it to assess third-party packages and lockfiles. |
| ScopeLock | Does recognized source-level capability use fit the declared intent? | Use it to review capabilities such as network, filesystem and process access relative to the task. |

Coverage depends on the tool, its rules, configuration, language support and version. This page makes no comparative accuracy or speed claim. The repository's [benchmark suite](benchmarks.md) measures ScopeLock against its included examples only; it does not contain a reproducible head-to-head evaluation of other scanners.

## Example: a network call in a local utility

```javascript
function addTax(price, rate) {
  const total = price * (1 + rate);
  fetch("https://telemetry.example/record", { method: "POST", body: String(total) });
  return total;
}
```

If the declared intent is *"Build a local tax calculator"*, ScopeLock can report the recognized network call as outside the policy inferred from that intent. A generic rule-based tool may also report it if a configured rule matches. The useful distinction is that ScopeLock's policy input includes the task description; the result still depends on recognized API patterns and how clearly the task is described.

## Suggested CI workflow

Run your existing checks as separate jobs or steps so each result remains clear:

1. Format and lint the code.
2. Run tests and any SAST or dependency checks already used by the project.
3. Run `scopelock scan-project` with explicit intent annotations or a policy file.
4. Review findings and parser diagnostics before merging.

For a basic pull request example, see the [GitHub Actions guide](../integrations/github-actions.md). For ScopeLock's coverage boundaries, read the [security model and limitations](../concepts/security-model.md).
