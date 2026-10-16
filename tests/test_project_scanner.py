"""Test suite for project-wide repository scanner."""

import subprocess

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


def test_scan_staged_reads_index_content_not_working_tree(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    source = tmp_path / "src" / "app.js"
    source.parent.mkdir()
    source.write_text(
        "// @intent: Local arithmetic calculator\nfetch('https://example.com');\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "src/app.js"], cwd=tmp_path, check=True)
    source.write_text("function add(a, b) { return a + b; }\n", encoding="utf-8")

    summary = ProjectScanner().scan_staged(str(tmp_path))

    assert summary.scanned_files == 1
    assert summary.violated_files == 1
    assert summary.file_reports[0].target_file == "src/app.js"


def test_scan_sources_honors_custom_default_intent():
    summary = ProjectScanner().scan_sources(
        {"src/app.js": "function add(a, b) { return a + b; }"},
        default_intent="Local arithmetic calculator",
    )

    assert summary.file_reports[0].policy.stated_intent == "Local arithmetic calculator"
