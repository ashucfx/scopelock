"""Tests for the public Python SDK."""

import pytest

from scopelock import ScopeLockClient
from scopelock.core.schema import AuditVerdict


def test_sdk_audits_source():
    report = ScopeLockClient(force_offline=True).audit(
        "fetch('https://evil.example')",
        "Build a local offline calculator",
    )

    assert report.final_verdict == AuditVerdict.FAILED
    assert report.target_file == "snippet.js"


def test_sdk_rejects_unknown_language():
    with pytest.raises(ValueError, match="Unsupported language"):
        ScopeLockClient().audit("puts 'hello'", "Build a utility", language="ruby")
