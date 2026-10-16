# How ScopeLock Fits with Other Analysis Tools

ScopeLock checks a narrow question: do the capability-bearing API patterns it recognizes appear authorized by the policy inferred from a task description? It can complement other code review and security analysis tools, but it does not replace them.

ScopeLock currently recognizes a finite set of JavaScript and Python API patterns. It does not establish program behavior, trace all data flows, identify every vulnerability, or prevent runtime effects. A clean report only means that the scanner found no unauthorized use among the patterns it recognized under the inferred policy.

The repository does not maintain a measured feature or performance comparison against ESLint, SonarQube, CodeQL, Semgrep, Snyk, or other analyzers. Their capabilities depend on versions, configuration, and rules; results from this project's small fixture suite should not be used to infer their outcomes.

## Suggested Use

Use ScopeLock's CLI or CI exit status as one review signal alongside tests and the security tools appropriate for the project. Treat `NEEDS_REVIEW`, parser diagnostics, and unsupported code patterns as reasons for manual review. Do not interpret the audit as a runtime sandbox or proof that code is safe.

See [fixture-suite checks](benchmarks.md) for the benchmark's scope and limitations.
