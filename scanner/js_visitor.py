"""
JavaScript / TypeScript AST Visitor for ScopeLock.

Uses Tree-sitter Concrete Syntax Tree traversal to identify security-sensitive
APIs, extract accurate source coordinates, and isolate potential capability over-reach.
"""

import tree_sitter_javascript as tsjs
from tree_sitter import Language, Node, Parser

from scopelock.core.schema import ObservedCapability, SourceLocation
from scopelock.core.taxonomy import (
    JS_SENSITIVE_APIS,
    CapabilityAction,
    CapabilityCategory,
)


class JavaScriptASTVisitor:
    """Deterministic AST visitor for JavaScript and TypeScript code."""

    def __init__(self):
        self.language = Language(tsjs.language())
        self.parser = Parser(self.language)

    def scan(self, code: str, file_name: str = "snippet.js") -> list[ObservedCapability]:
        """Parse JavaScript code string and return list of observed capabilities."""
        code_bytes = code.encode("utf-8")
        tree = self.parser.parse(code_bytes)
        capabilities: list[ObservedCapability] = []

        self._traverse(tree.root_node, code_bytes, file_name, capabilities)
        return capabilities

    def _traverse(
        self, node: Node, code_bytes: bytes, file_name: str, results: list[ObservedCapability]
    ) -> None:
        """Recursively traverse AST nodes."""
        # 1. Inspect function call invocations
        if node.type == "call_expression":
            self._handle_call_expression(node, code_bytes, file_name, results)

        # 2. Inspect sensitive member access (e.g. process.env)
        elif node.type == "member_expression":
            self._handle_member_expression(node, code_bytes, file_name, results)

        for child in node.children:
            self._traverse(child, code_bytes, file_name, results)

    def _handle_call_expression(
        self, node: Node, code_bytes: bytes, file_name: str, results: list[ObservedCapability]
    ) -> None:
        """Analyze call_expression nodes for sensitive APIs."""
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

        # Extract first argument target (e.g. URL or filename) if present
        target_scope = self._extract_first_arg(node, code_bytes)

        # Match against sensitive API table
        for pattern, (category, action, _) in JS_SENSITIVE_APIS.items():
            matched = False
            if "." in pattern:
                # E.g. "fs.readFile" or "child_process.exec"
                if pattern in call_ident or call_ident.endswith(pattern):
                    matched = True
            else:
                # Direct call like "fetch" or "eval"
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
                break  # Matched most specific pattern

    def _handle_member_expression(
        self, node: Node, code_bytes: bytes, file_name: str, results: list[ObservedCapability]
    ) -> None:
        """Detect access to process.env.* for secrets auditing."""
        expr_text = (
            code_bytes[node.start_byte : node.end_byte].decode("utf-8", errors="replace").strip()
        )
        if expr_text.startswith("process.env") and expr_text != "process.env":
            loc = SourceLocation(
                file=file_name,
                line=node.start_point[0] + 1,
                col=node.start_point[1],
                end_line=node.end_point[0] + 1,
                end_col=node.end_point[1],
                snippet=expr_text,
            )
            # Avoid duplicate reporting if parent is also a member_expression
            if (
                node.parent
                and node.parent.type == "member_expression"
                and node.parent.start_byte == node.start_byte
            ):
                return

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
        """Extract literal string value of first argument if available."""
        args_node = call_node.child_by_field_name("arguments")
        if not args_node or args_node.named_child_count == 0:
            return None

        first_arg = args_node.named_children[0]
        if first_arg.type in ("string", "template_string"):
            text = code_bytes[first_arg.start_byte : first_arg.end_byte].decode(
                "utf-8", errors="replace"
            )
            return text.strip("\"'`")
        return None
