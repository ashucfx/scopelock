"""Test suite for project-wide repository scanner."""

import pytest

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


@pytest.mark.parametrize(
    "contents, message",
    [
        ("{ invalid", "Invalid JSON"),
        ("[]", "JSON object"),
        ('{"modules": []}', "modules"),
        ('{"modules": {"src/app.py": {}}}', "non-empty string 'intent'"),
    ],
)
def test_invalid_policy_files_raise_instead_of_falling_back(tmp_path, contents, message):
    policy_file = tmp_path / "scopelock.json"
    policy_file.write_text(contents, encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        ProjectScanner(policy_file=str(policy_file))


def test_missing_policy_file_raises_instead_of_falling_back(tmp_path):
    missing_policy = tmp_path / "missing.json"

    with pytest.raises(OSError, match="Cannot read policy file"):
        ProjectScanner(policy_file=str(missing_policy))
