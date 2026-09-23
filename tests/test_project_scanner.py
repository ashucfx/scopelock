"""Test suite for project-wide repository scanner."""

from scopelock.core.project_scanner import ProjectScanner


def test_in_code_intent_extraction():
    """Verify that in-code // @intent: comments are extracted accurately."""
    code_js = """
    // @intent: Local mathematical calculator for arithmetic
    function add(a, b) {
        return a + b;
    }
    """
    scanner = ProjectScanner()
    intent = scanner.extract_in_code_intent(code_js)
    assert intent == "Local mathematical calculator for arithmetic"


def test_python_in_code_intent_extraction():
    """Verify that Python # @intent: comments are extracted."""
    code_py = """
    # @intent: Pure string formatting utility
    def format_title(s):
        return s.title()
    """
    scanner = ProjectScanner()
    intent = scanner.extract_in_code_intent(code_py)
    assert intent == "Pure string formatting utility"
