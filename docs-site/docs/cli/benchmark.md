# `scopelock benchmark`

Run regression checks against the repository's curated source fixture suite.

## Synopsis

```bash
scopelock benchmark
```

The suite contains 25 hand-curated JavaScript fixtures. Each is labeled with the expected number of unauthorized capability findings. The runner compares labels with the current audit output and reports **program-level** classification: a positive fixture counts as detected when at least one violation is reported. It does not measure which individual events were detected or partial coverage within a fixture.

The printed latency measures AST parsing only. It excludes intent decomposition, policy alignment, report formatting, file reads, and project traversal. Timing depends on the environment.

These results help catch regressions in the included examples. They do not estimate real-world detection performance, and this project does not provide measured comparisons against other static analyzers.

## Dataset

The fixture code, task prompt, expected violation count, and category label are maintained in [`benchmarks/dataset.py`](https://github.com/ashucfx/scopelock/blob/main/benchmarks/dataset.py). Review the source to understand the current test coverage and its limits.
