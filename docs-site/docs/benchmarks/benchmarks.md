# Fixture-Suite Checks

The repository contains 25 curated source fixtures in [`benchmarks/dataset.py`](https://github.com/ashucfx/scopelock/blob/main/benchmarks/dataset.py): 11 are labeled without unauthorized capabilities and 14 with at least one. Run `scopelock benchmark` to check the implementation against these fixtures.

The runner reports program-level classification. A positive fixture is counted as detected when the audit reports at least one violation; the score does not measure per-event precision or partial coverage. These fixtures are regression checks and do not estimate real-world detection performance.

The reported timing measures AST parsing only. It excludes prompt decomposition, policy alignment, report formatting, file reads, and project traversal. Results depend on the machine and environment running the command.

No comparative evaluation against ESLint, SonarQube, CodeQL, Semgrep, or other analyzers is maintained by this project. Their results should not be inferred from this fixture suite.

## Running the Checks

```bash
scopelock benchmark
python -m scopelock.benchmarks.runner
pytest tests/ -k benchmark
```

The source fixtures and their expected program-level labels are maintained in [`benchmarks/dataset.py`](https://github.com/ashucfx/scopelock/blob/main/benchmarks/dataset.py). The labels are hand-curated regression data, not an independently annotated evaluation corpus.
