"""
Unified Scanner Engine for ScopeLock.

Dispatches source code to the appropriate language AST visitor,
measures execution latency, and standardizes extracted capabilities.
"""

import time

from scopelock.core.schema import ObservedCapability, ScanDiagnostic, SourceLocation
from scopelock.scanner.js_visitor import JavaScriptASTVisitor
from scopelock.scanner.py_visitor import PythonASTVisitor


class ScannerEngine:
    """Multi-language static AST scanning engine."""

    def __init__(self):
        self.js_visitor = JavaScriptASTVisitor()
        self.py_visitor = PythonASTVisitor()

    def scan_code(
        self, code: str, file_name: str = "snippet.js"
    ) -> tuple[list[ObservedCapability], float]:
        """
        Scan code string and return (capabilities, latency_ms).
        """
        start = time.perf_counter()

        if file_name.endswith((".py", ".python")):
            caps = self.py_visitor.scan(code, file_name=file_name)
        else:
            # Default to JavaScript/TypeScript parser
            caps = self.js_visitor.scan(code, file_name=file_name)

        latency_ms = (time.perf_counter() - start) * 1000.0
        return caps, latency_ms

    def scan_code_detailed(
        self, code: str, file_name: str = "snippet.js"
    ) -> tuple[list[ObservedCapability], float, list[ScanDiagnostic]]:
        """Scan source and return capabilities plus parser diagnostics."""
        start = time.perf_counter()
        visitor = self.py_visitor if file_name.endswith((".py", ".python")) else self.js_visitor
        caps, error_nodes = visitor.scan_detailed(code, file_name=file_name)
        diagnostics = [
            ScanDiagnostic(
                message=f"Parser reported an error node: {node.text.decode('utf-8', errors='replace')[:120]}",
                source_location=SourceLocation(
                    file=file_name,
                    line=node.start_point[0] + 1,
                    col=node.start_point[1],
                    end_line=node.end_point[0] + 1,
                    end_col=node.end_point[1],
                ),
            )
            for node in error_nodes
        ]
        return caps, (time.perf_counter() - start) * 1000.0, diagnostics

    def scan_file(self, file_path: str) -> tuple[list[ObservedCapability], float]:
        """Scan a file on the local filesystem."""
        caps, latency_ms, _ = self.scan_file_detailed(file_path)
        return caps, latency_ms

    def scan_file_detailed(
        self, file_path: str
    ) -> tuple[list[ObservedCapability], float, list[ScanDiagnostic]]:
        """Scan a file and preserve parser diagnostics for fail-closed callers."""
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return self.scan_code_detailed(content, file_name=file_path)
