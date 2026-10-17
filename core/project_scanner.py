"""
Project-Wide Scanner and In-Code Intent Extractor for ScopeLock.

Enables enterprise CI/CD and developer workflows by scanning entire repositories,
extracting in-code intent headers (// @intent: ...), and enforcing scopelock.json policies.
"""

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from scopelock.core.aligner import CapabilityAligner
from scopelock.core.intent_engine import IntentDecomposer
from scopelock.core.schema import AuditReport, AuditVerdict
from scopelock.scanner.engine import ScannerEngine


class PolicyConfigError(ValueError):
    """Raised when a project policy file is unreadable or invalid."""


@dataclass
class ProjectAuditSummary:
    """Aggregated audit results across an entire codebase."""
    scanned_files: int = 0
    clean_files: int = 0
    violated_files: int = 0
    needs_review_files: int = 0
    total_violations: int = 0
    total_latency_ms: float = 0.0
    file_reports: list[AuditReport] = field(default_factory=list)
    skipped_files: list[str] = field(default_factory=list)
    scan_errors: list[str] = field(default_factory=list)
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
        """Load and validate scopelock.json project configuration."""
        path = Path(path_str)
        try:
            with open(path, "r", encoding="utf-8") as f:
                policy = json.load(f)
        except json.JSONDecodeError as exc:
            raise PolicyConfigError(f"Invalid JSON in policy file '{path}': {exc}") from exc
        except OSError as exc:
            raise OSError(f"Cannot read policy file '{path}': {exc}") from exc

        if not isinstance(policy, dict):
            raise PolicyConfigError("Policy file must contain a JSON object.")
        modules = policy.get("modules", {})
        if not isinstance(modules, dict):
            raise PolicyConfigError("Policy field 'modules' must contain an object.")
        for module_path, module_policy in modules.items():
            if not isinstance(module_path, str) or not isinstance(module_policy, dict):
                raise PolicyConfigError("Each policy module must map a path to an object.")
            intent = module_policy.get("intent")
            if not isinstance(intent, str) or not intent.strip():
                raise PolicyConfigError(
                    f"Policy module '{module_path}' must define a non-empty string 'intent'."
                )
        return policy

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
        default_intent: str | None = None,
    ) -> ProjectAuditSummary:
        """Recursively scan source files from a working tree."""
        root = Path(directory_path)
        if not root.exists() or not root.is_dir():
            return ProjectAuditSummary(
                scan_errors=[
                    f"Directory does not exist or is not a directory: {directory_path}"
                ],
                verdict=AuditVerdict.NEEDS_REVIEW,
            )

        sources: dict[str, str] = {}
        skipped_files: list[str] = []
        scan_errors: list[str] = []
        for file_path in root.rglob("*"):
            if not file_path.is_file() or file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue
            relative_path = file_path.relative_to(root)
            if any(ignored in relative_path.parts for ignored in self.IGNORE_DIRS):
                continue
            rel_path = str(relative_path).replace("\\", "/")
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    sources[rel_path] = f.read()
            except OSError as exc:
                skipped_files.append(rel_path)
                scan_errors.append(f"{rel_path}: {exc}")
        return self.scan_sources(
            sources,
            default_intent=default_intent,
            skipped_files=skipped_files,
            scan_errors=scan_errors,
        )

    def scan_staged(self, repository_path: str = ".") -> ProjectAuditSummary:
        """Audit supported source files exactly as staged in the Git index."""
        try:
            root = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=repository_path,
                capture_output=True,
                check=True,
                text=True,
            ).stdout.strip()
            staged_paths = subprocess.run(
                [
                    "git",
                    "diff",
                    "--cached",
                    "--no-renames",
                    "--name-only",
                    "--diff-filter=ACMRT",
                    "-z",
                ],
                cwd=root,
                capture_output=True,
                check=True,
            ).stdout.decode("utf-8", errors="replace").split("\0")
        except (OSError, subprocess.CalledProcessError) as exc:
            return ProjectAuditSummary(
                scan_errors=[f"Unable to read staged Git files: {exc}"],
                verdict=AuditVerdict.NEEDS_REVIEW,
            )

        sources: dict[str, str] = {}
        skipped_files: list[str] = []
        scan_errors: list[str] = []
        for rel_path in filter(None, staged_paths):
            path = Path(rel_path)
            if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue
            if any(ignored in path.parts for ignored in self.IGNORE_DIRS):
                continue
            try:
                result = subprocess.run(
                    ["git", "show", f":{rel_path}"],
                    cwd=root,
                    capture_output=True,
                    check=True,
                )
                sources[rel_path.replace("\\", "/")] = result.stdout.decode(
                    "utf-8", errors="replace"
                )
            except (OSError, subprocess.CalledProcessError) as exc:
                skipped_files.append(rel_path)
                scan_errors.append(f"{rel_path}: unable to read staged content: {exc}")
        return self.scan_sources(sources, skipped_files=skipped_files, scan_errors=scan_errors)

    def scan_sources(
        self,
        sources: dict[str, str],
        default_intent: str | None = None,
        skipped_files: list[str] | None = None,
        scan_errors: list[str] | None = None,
    ) -> ProjectAuditSummary:
        """Audit a mapping of repository-relative paths to source contents."""
        summary = ProjectAuditSummary(
            skipped_files=skipped_files or [],
            scan_errors=scan_errors or [],
        )
        for rel_path, code in sources.items():
            path = Path(rel_path)
            if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue
            if any(ignored in path.parts for ignored in self.IGNORE_DIRS):
                continue

            intent = self.extract_in_code_intent(code)
            if not intent and rel_path in self.policy_data.get("modules", {}):
                intent = self.policy_data["modules"][rel_path].get("intent")
            if not intent:
                if default_intent:
                    intent = default_intent
                else:
                    stem = path.stem.replace("_", " ").replace("-", " ")
                    intent = f"Module for {stem}"

            caps, latency, diagnostics = self.scanner.scan_code_detailed(code, file_name=rel_path)
            policy = IntentDecomposer.decompose(intent)
            report = CapabilityAligner.align(
                policy=policy,
                observed_caps=caps,
                target_file=rel_path,
                latency_ms=latency,
                diagnostics=diagnostics,
            )
            summary.scanned_files += 1
            summary.total_latency_ms += latency
            summary.file_reports.append(report)

            if report.final_verdict == AuditVerdict.FAILED:
                summary.violated_files += 1
                summary.total_violations += report.total_violations
            elif report.final_verdict == AuditVerdict.NEEDS_REVIEW:
                summary.needs_review_files += 1
            else:
                summary.clean_files += 1

        if summary.violated_files > 0:
            summary.verdict = AuditVerdict.FAILED
        elif summary.scan_errors or any(
            report.has_blocking_diagnostics() for report in summary.file_reports
        ):
            summary.verdict = AuditVerdict.NEEDS_REVIEW
        else:
            summary.verdict = AuditVerdict.PASSED
        return summary
