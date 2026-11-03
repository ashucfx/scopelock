"""Stable Python API for ScopeLock audits."""

from pathlib import Path

from scopelock.core.aligner import CapabilityAligner
from scopelock.core.intent_engine import IntentDecomposer
from scopelock.core.project_scanner import ProjectAuditSummary, ProjectScanner
from scopelock.core.schema import AuditReport
from scopelock.scanner.engine import ScannerEngine


class ScopeLockClient:
    """High-level client for source and repository audits."""

    def __init__(self, *, force_offline: bool = False):
        self.force_offline = force_offline
        self.scanner = ScannerEngine()

    def audit(self, code: str, prompt: str, *, language: str = "js") -> AuditReport:
        """Audit a source string against a developer requirement."""
        extension = self._normalize_language(language)
        file_name = f"snippet.{extension}"
        caps, latency, diagnostics = self.scanner.scan_code_detailed(code, file_name=file_name)
        policy = IntentDecomposer.decompose(prompt, force_offline=self.force_offline)
        return CapabilityAligner.align(
            policy=policy,
            observed_caps=caps,
            target_file=file_name,
            latency_ms=latency,
            diagnostics=diagnostics,
        )

    def audit_file(self, path: str | Path, prompt: str) -> AuditReport:
        """Audit a source file while preserving its path in findings."""
        source_path = Path(path)
        code = source_path.read_text(encoding="utf-8", errors="replace")
        extension = self._normalize_language(source_path.suffix.lstrip("."))
        caps, latency, diagnostics = self.scanner.scan_code_detailed(
            code, file_name=str(source_path)
        )
        policy = IntentDecomposer.decompose(prompt, force_offline=self.force_offline)
        return CapabilityAligner.align(
            policy=policy,
            observed_caps=caps,
            target_file=str(source_path),
            latency_ms=latency,
            diagnostics=diagnostics,
        )

    def audit_project(
        self, directory: str | Path, *, policy_file: str | Path | None = None
    ) -> ProjectAuditSummary:
        """Audit all supported source files in a repository directory."""
        scanner = ProjectScanner(policy_file=str(policy_file) if policy_file else None)
        return scanner.scan_directory(str(directory))

    @staticmethod
    def _normalize_language(language: str) -> str:
        normalized = language.lower().lstrip(".")
        if normalized in {"javascript", "typescript", "js", "ts", "jsx", "tsx", "mjs", "cjs"}:
            return "js"
        if normalized in {"python", "py"}:
            return "py"
        raise ValueError(f"Unsupported language '{language}'. Use JavaScript/TypeScript or Python.")


__all__ = ["ScopeLockClient"]
