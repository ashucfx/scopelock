# Python SDK

Use ScopeLock programmatically in your Python applications and scripts.

## Installation

```bash
pip install scopelock
```

## Core Modules

### `ScannerEngine`

Scan code strings or files and extract observed capabilities.

```python
from scopelock.scanner.engine import ScannerEngine

scanner = ScannerEngine()

# Scan a JavaScript code string
caps, latency_ms = scanner.scan_code(
    code="fetch('https://evil.com')",
    file_name="snippet.js"
)

# Scan a file on disk
caps, latency_ms = scanner.scan_file("path/to/app.py")

print(f"Found {len(caps)} capabilities in {latency_ms:.2f}ms")
for cap in caps:
    print(f"  {cap.category.value} — {cap.raw_call} @ line {cap.source_location.line}")
```

---

### `IntentDecomposer`

Convert a natural language prompt into a `ScopePolicy`.

```python
from scopelock.core.intent_engine import IntentDecomposer

policy = IntentDecomposer.decompose(
    prompt="Build a local offline arithmetic calculator"
)

print(policy.allowed_categories)    # set()
print(policy.disallowed_categories) # {NETWORK, FILESYSTEM, PROCESS, ...}
print(policy.is_ambiguous)          # False

# Force offline (skip LLM even if API key is set):
policy = IntentDecomposer.decompose(prompt="...", force_offline=True)
```

---

### `CapabilityAligner`

Compare observed capabilities against a policy to produce an audit report.

```python
from scopelock.core.aligner import CapabilityAligner

report = CapabilityAligner.align(
    policy=policy,
    observed_caps=caps,
    target_file="app.js",
    latency_ms=latency_ms
)

print(report.final_verdict)        # AuditVerdict.FAILED or PASSED
print(report.total_violations)     # int
for finding in report.findings:
    print(f"{finding.verdict.value}: {finding.finding}")
```

---

### Full Pipeline Example

```python
from scopelock.scanner.engine import ScannerEngine
from scopelock.core.intent_engine import IntentDecomposer
from scopelock.core.aligner import CapabilityAligner
from scopelock.core.reporter import ReportFormatter
from scopelock.core.schema import AuditVerdict

def audit(code: str, prompt: str, lang: str = "js") -> bool:
    """Returns True if code passes, False if violations detected."""
    scanner = ScannerEngine()
    caps, latency = scanner.scan_code(code, file_name=f"snippet.{lang}")
    
    policy = IntentDecomposer.decompose(prompt)
    report = CapabilityAligner.align(policy, caps, latency_ms=latency)
    
    print(ReportFormatter.to_terminal(report))
    return report.final_verdict == AuditVerdict.PASSED


# Example usage:
code = """
function calcTotal(price, tax) {
    fetch("https://evil.com");  // Injected
    return price * (1 + tax);
}
"""

passed = audit(code, "Build a local arithmetic calculator", "js")
if not passed:
    raise SystemExit("Security violation detected — deployment blocked")
```

---

### `ProjectScanner`

Scan entire directories recursively.

```python
from scopelock.core.project_scanner import ProjectScanner

scanner = ProjectScanner(policy_file="scopelock.json")
summary = scanner.scan_directory("./src")

print(f"Scanned: {summary.scanned_files}")
print(f"Clean:   {summary.clean_files}")
print(f"Failed:  {summary.violated_files}")
print(f"Verdict: {summary.verdict}")
```

---

### `PDFReportGenerator`

Generate a professional PDF audit report.

```python
from scopelock.core.pdf_generator import PDFReportGenerator

pdf_bytes = PDFReportGenerator.generate(report)

with open("audit-report.pdf", "wb") as f:
    f.write(pdf_bytes)
```

---

## Data Models

All models are Pydantic v2 `BaseModel` subclasses, fully typed and serializable:

```python
from scopelock.core.schema import (
    AuditReport,       # Final audit output
    AuditVerdict,      # PASSED / FAILED / NEEDS_REVIEW
    ScopePolicy,       # Expected capability contract
    DivergenceFinding, # Individual finding with risk score
    ObservedCapability,# Capability detected in code
    SourceLocation,    # File + line + column
    RiskTier,          # JUSTIFIED / UNJUSTIFIED / SUSPICIOUS / AMBIGUOUS
)

from scopelock.core.taxonomy import (
    CapabilityCategory, # NETWORK / FILESYSTEM / PROCESS / SECRET / DATABASE / RUNTIME
    CapabilityAction,   # NET_REQUEST / FS_READ / PROC_EXEC / etc.
)
```
