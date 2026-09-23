"""Test suite for Python AST visitor."""

import pytest
from scopelock.scanner.py_visitor import PythonASTVisitor
from scopelock.core.taxonomy import CapabilityCategory


@pytest.fixture
def visitor():
    return PythonASTVisitor()


def test_python_ignores_comments_and_strings(visitor):
    """Python AST must ignore comments and string literals."""
    code = """
    # os.system('rm -rf /')
    note = "requests.get('https://fake.com')"
    x = 10 + 20
    """
    caps = visitor.scan(code, file_name="script.py")
    assert len(caps) == 0


def test_python_detects_system_and_requests(visitor):
    """Python AST detects os.system and requests.get calls."""
    code = """
    import os
    import requests

    def run():
        requests.get("https://api.example.com/status")
        os.system("ls -la")
    """
    caps = visitor.scan(code, file_name="run.py")
    assert len(caps) == 2
    cats = {c.category for c in caps}
    assert CapabilityCategory.NETWORK in cats
    assert CapabilityCategory.PROCESS in cats
