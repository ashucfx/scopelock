"""
Project-Wide Scanner and In-Code Intent Extractor for ScopeLock.

Enables enterprise CI/CD and developer workflows by scanning entire repositories,
extracting in-code intent headers (// @intent: ...), and enforcing scopelock.json policies.
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from scopelock.core.aligner import CapabilityAligner
from scopelock.core.intent_engine import IntentDecomposer
from scopelock.core.schema import AuditReport, AuditVerdict
from scopelock.scanner.engine import ScannerEngine


@dataclass
class ProjectAuditSummary:
    """Aggregated audit results across an entire codebase."""
    scanned_files: int = 0
    clean_files: int = 0
    violated_files: int = 0
    total_violations: int = 0
    total_latency_ms: float = 0.0
    file_reports: list[AuditReport] = field(default_factory=list)
    verdict: AuditVerdict = AuditVerdict.PASSED


class ProjectScanner:
    """Audits entire software repositories recursively."""

    INTENT_COMMENT_REGEX: ClassVar[tuple[re.Pattern, ...]] = (
        re.compile(r"//\s*@intent:\s*(.+)", re.IGNORECASE),
        re.compile(r"/\*\s*@intent:\s*(.+?)\*/", re.IGNORECASE | re.DOTALL),
        re.compile(r"#\s*@intent:\s*(.+)", re.IGNORECASE),
        re.compile(r'"""\s*@intent:\s*(.+?)"""', re.IGNORECASE | re.DOTALL),
    )

    SUPPORTED_EXTENSIONS: ClassVar[tuple[str, ...]] = (
        ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".py"
    )

    IGNORE_DIRS: ClassVar[tuple[str, ...]] = (
        "node_modules", ".git", ".venv", "venv", "__pycache__", "dist", "build", ".next"
    )

    def __init__(self, policy_file: str | None = None):
        self.scanner = ScannerEngine()
        self.policy_data = self._load_policy(policy_file) if policy_file else {}

    def _load_policy(self, path_str: str) -> dict:
        """Load optional scopelock.json project configuration."""
        path = Path(path_str)
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError):
                return {}
        return {}

    def extract_in_code_intent(self, content: str) -> str | None:
        """Extract declared @intent header comment from source code."""
        # Check first 25 lines for efficiency
        header_text = "\n".join(content.splitlines()[:25])
        for pattern in self.INTENT_COMMENT_REGEX:
            match = pattern.search(header_text)
            if match:
                return match.group(1).strip()
        return None

    def scan_directory(
        self,
        directory_path: str,
        default_intent: str = "General application module"
    ) -> ProjectAuditSummary:
        """Recursively scan an entire codebase folder."""
        root = Path(directory_path)
        summary = ProjectAuditSummary()

        if not root.exists():
            return summary

        for file_path in root.rglob("*"):
            if file_path.is_file() and file_path.suffix in self.SUPPORTED_EXTENSIONS:
                # Skip ignored directories
                if any(ignored in file_path.parts for ignored in self.IGNORE_DIRS):
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        code = f.read()
                except OSError:
                    continue

                # 1. Determine intent: in-code header -> policy file -> default
                rel_path = str(file_path.relative_to(root)).replace("\\", "/")
                intent = self.extract_in_code_intent(code)

                if not intent and rel_path in self.policy_data.get("modules", {}):
                    intent = self.policy_data["modules"][rel_path].get("intent")

                if not intent:
                    # Infer intent from filename if no explicit annotation
                    stem = file_path.stem.replace("_", " ").replace("-", " ")
                    intent = f"Module for {stem}"

                # 2. Run AST scan and alignment
                caps, lat = self.scanner.scan_code(code, file_name=rel_path)
                policy = IntentDecomposer.decompose(intent)
                report = CapabilityAligner.align(
                    policy=policy,
                    observed_caps=caps,
                    target_file=rel_path,
                    latency_ms=lat
                )

                summary.scanned_files += 1
                summary.total_latency_ms += lat
                summary.file_reports.append(report)

                if report.final_verdict == AuditVerdict.FAILED:
                    summary.violated_files += 1
                    summary.total_violations += report.total_violations
                else:
                    summary.clean_files += 1

        if summary.violated_files > 0:
            summary.verdict = AuditVerdict.FAILED
        else:
            summary.verdict = AuditVerdict.PASSED

        return summary
