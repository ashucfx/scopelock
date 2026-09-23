"""
Python AST Visitor for ScopeLock.

Uses Tree-sitter Concrete Syntax Tree traversal to identify security-sensitive
Python APIs (subprocess, os.system, requests, open, os.environ).
"""

import tree_sitter_python as tspy
from tree_sitter import Language, Node, Parser

from scopelock.core.schema import ObservedCapability, SourceLocation
from scopelock.core.taxonomy import (
    PY_SENSITIVE_APIS,
    CapabilityAction,
    CapabilityCategory,
)


class PythonASTVisitor:
    """Deterministic AST visitor for Python source code."""

    def __init__(self):
        self.language = Language(tspy.language())
        self.parser = Parser(self.language)

    def scan(self, code: str, file_name: str = "script.py") -> list[ObservedCapability]:
        """Parse Python code string and return observed capabilities."""
        code_bytes = code.encode("utf-8")
        tree = self.parser.parse(code_bytes)
        capabilities: list[ObservedCapability] = []

        self._traverse(tree.root_node, code_bytes, file_name, capabilities)
        return capabilities

    def _traverse(
        self, node: Node, code_bytes: bytes, file_name: str, results: list[ObservedCapability]
    ) -> None:
        """Recursively traverse AST nodes."""
        if node.type == "call":
            self._handle_call(node, code_bytes, file_name, results)
        elif node.type == "attribute":
            self._handle_attribute(node, code_bytes, file_name, results)

        for child in node.children:
            self._traverse(child, code_bytes, file_name, results)

    def _handle_call(
        self, node: Node, code_bytes: bytes, file_name: str, results: list[ObservedCapability]
    ) -> None:
        """Inspect Python function calls."""
        func_node = node.child_by_field_name("function")
        if not func_node:
            return

        call_ident = (
            code_bytes[func_node.start_byte : func_node.end_byte]
            .decode("utf-8", errors="replace")
            .strip()
        )
        raw_call = (
            code_bytes[node.start_byte : node.end_byte].decode("utf-8", errors="replace").strip()
        )
        target_scope = self._extract_first_arg(node, code_bytes)

        for pattern, (category, action, _) in PY_SENSITIVE_APIS.items():
            matched = False
            if "." in pattern:
                if pattern in call_ident or call_ident.endswith(pattern):
                    matched = True
            else:
                if call_ident == pattern or call_ident.endswith(f".{pattern}"):
                    matched = True

            if matched:
                loc = SourceLocation(
                    file=file_name,
                    line=node.start_point[0] + 1,
                    col=node.start_point[1],
                    end_line=node.end_point[0] + 1,
                    end_col=node.end_point[1],
                    snippet=raw_call[:120],
                )
                results.append(
                    ObservedCapability(
                        category=category,
                        action=action,
                        source_location=loc,
                        raw_call=call_ident,
                        target_scope=target_scope or "*",
                        confidence=0.98,
                        origin="STATIC_AST",
                    )
                )
                break

    def _handle_attribute(
        self, node: Node, code_bytes: bytes, file_name: str, results: list[ObservedCapability]
    ) -> None:
        """Detect os.environ attribute accesses."""
        expr_text = (
            code_bytes[node.start_byte : node.end_byte].decode("utf-8", errors="replace").strip()
        )
        if expr_text.startswith("os.environ"):
            loc = SourceLocation(
                file=file_name,
                line=node.start_point[0] + 1,
                col=node.start_point[1],
                end_line=node.end_point[0] + 1,
                end_col=node.end_point[1],
                snippet=expr_text,
            )
            results.append(
                ObservedCapability(
                    category=CapabilityCategory.SECRET,
                    action=CapabilityAction.SECRET_READ_ENV,
                    source_location=loc,
                    raw_call=expr_text,
                    target_scope=expr_text.split(".")[-1],
                    confidence=0.99,
                    origin="STATIC_AST",
                )
            )

    def _extract_first_arg(self, call_node: Node, code_bytes: bytes) -> str | None:
        """Extract first string argument in Python call."""
        args_node = call_node.child_by_field_name("arguments")
        if not args_node or args_node.named_child_count == 0:
            return None

        first_arg = args_node.named_children[0]
        if first_arg.type == "string":
            text = code_bytes[first_arg.start_byte : first_arg.end_byte].decode(
                "utf-8", errors="replace"
            )
            return text.strip("\"'")
        return None
