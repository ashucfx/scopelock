# Benchmark suite

ScopeLock ships with a fixed, locally runnable set of 25 source examples. The suite is useful for checking expected behavior while changing scanner or policy code. It is an engineering fixture, not a representative sample of all software.

## Dataset

The cases are defined in [`benchmarks/dataset.py`](https://github.com/ashucfx/scopelock/blob/main/benchmarks/dataset.py). The current set contains 11 examples classified as clean and 14 examples with an expected capability finding. Cases use short JavaScript snippets and cover common filesystem, network, process, database, secret and runtime patterns.

The dataset is intentionally small and manually curated. It does not model the prevalence of findings in real repositories, complex control flow, dependency behavior or every supported language and API. Its labels are the expected outcomes for these examples, not an independent security ground truth.

## Run it locally

From an installed checkout:

```bash
scopelock benchmark
```

Or run the module from the source checkout:

```bash
python -m scopelock.benchmarks.runner
```

The command prints the case results followed by aggregate counts and timing. The runner scans every example and compares the number of findings with whether the case is labeled as having zero or non-zero expected findings.

## Read the metrics carefully

| Metric | What the runner counts |
|---|---|
| True positive / false negative | Cases labeled with a finding where ScopeLock reports at least one / none |
| True negative / false positive | Cases labeled clean where ScopeLock reports none / at least one |
| Precision, recall and F1 | Case-level aggregates computed from those counts |
| Average latency | Mean time spent in `ScannerEngine.scan_code` for the examples |

The current runner classifies at the **case level**: any finding on a positive case counts as detected, regardless of whether the exact category or location matches. Timing excludes intent decomposition, file I/O, process startup and CI setup. Results vary by machine and interpreter.

!!! note "Do not read benchmark scores as production guarantees"
    High scores on this fixed set show that the checked examples behave as expected. They do not predict detection rates or false-positive rates on an arbitrary codebase. Review findings and evaluate ScopeLock against your own representative code before using it as a release gate.

## Comparing tools

ScopeLock answers a different question from linters, dependency checkers and general SAST tools: it compares recognized source-level capabilities with a declared intent. It is designed to complement those tools. This repository does not currently provide a reproducible, version-pinned head-to-head benchmark against other scanners. See [how ScopeLock fits with other checks](comparison.md) for a qualitative guide.
