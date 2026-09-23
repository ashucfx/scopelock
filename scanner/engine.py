"""
Unified Scanner Engine for ScopeLock.

Dispatches source code to the appropriate language AST visitor,
measures execution latency, and standardizes extracted capabilities.
"""

import time

from scopelock.core.schema import ObservedCapability
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

    def scan_file(self, file_path: str) -> tuple[list[ObservedCapability], float]:
        """Scan a file on the local filesystem."""
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return self.scan_code(content, file_name=file_path)
