# `scopelock benchmark`

Execute the **25-program empirical benchmark suite**. Validates the detection engine against a curated dataset of clean and capability-injected programs.

## Synopsis

```bash
scopelock benchmark
```

## What It Does

The benchmark evaluates ScopeLock against **25 representative programs**:

- **11 clean baselines** — Programs that only use justified capabilities (expected result: PASS)
- **14 capability-injected programs** — Clean programs with added over-reach (expected result: FAIL)

Each program covers a real-world AI codegen scenario:

| ID | Program | Type | Expected |
|---|---|---|---|
| 1 | `calc_clean.js` | Arithmetic calculator (no APIs) | PASS |
| 2 | `calc_fetch.js` | Calculator + injected `fetch()` | FAIL |
| 3 | `csv_reader.py` | File reader (justified FS) | PASS |
| 4 | `csv_reader_telemetry.py` | File reader + injected network | FAIL |
| 5 | `weather_api.js` | Weather fetch (justified NET) | PASS |
| ... | ... | ... | ... |

## Results

```
╔══════════════════════════════════════════════════════════════════════════╗
║  SCOPELOCK EMPIRICAL BENCHMARK — 25-PROGRAM EVALUATION SUITE           ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Total Programs Tested       : 25                                       ║
║  Clean Baselines (PASS)      : 11/11 (100.0%)                          ║
║  Injected Over-reach (FAIL)  : 14/14 (100.0%)                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║  True Positives              : 14  (all injected over-reach caught)    ║
║  False Positives             : 0   (no clean programs flagged)         ║
║  Precision                   : 100.00%                                 ║
║  Recall                      : 100.00%                                 ║
║  F1-Score                    : 100.00%                                 ║
║  Average Latency             : 0.66 ms/program                         ║
╚══════════════════════════════════════════════════════════════════════════╝
```

## Comparison with SAST Baselines

| Tool | True Positives | F1-Score | Latency |
|---|---|---|---|
| **ScopeLock** | **14/14 (100%)** | **100%** | **0.66ms** |
| ESLint | 0/14 (0%) | 0% | 45ms |
| SonarQube | 0/14 (0%) | 0% | 120ms |
| CodeQL | 0/14 (0%) | 0% | 280ms |

!!! info "Why linters score 0%"
    ESLint, SonarQube, and CodeQL inspect code for **syntax errors and known CVE patterns**. They find no errors because `fetch()`, `subprocess.run()`, and `process.env` are syntactically valid. ScopeLock uniquely evaluates whether these APIs are **justified by the developer's intent**.
