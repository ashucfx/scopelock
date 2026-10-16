"""Tests for aggregate project report serialization."""

import json

from scopelock.core.project_scanner import ProjectAuditSummary
from scopelock.core.reporter import ReportFormatter
from scopelock.core.schema import AuditVerdict


def test_project_json_contains_summary_and_file_reports():
    summary = ProjectAuditSummary(scanned_files=2, clean_files=2)
    document = json.loads(ReportFormatter.to_project_json(summary))

    assert document["scanned_files"] == 2
    assert document["verdict"] == "PASSED"
    assert document["file_reports"] == []


def test_empty_project_sarif_is_valid():
    summary = ProjectAuditSummary()
    document = json.loads(ReportFormatter.to_project_sarif(summary))

    assert document["version"] == "2.1.0"
    assert document["runs"][0]["results"] == []


def test_project_sarif_preserves_scan_errors():
    summary = ProjectAuditSummary(
        scan_errors=["Unable to read staged file"],
        verdict=AuditVerdict.NEEDS_REVIEW,
    )

    document = json.loads(ReportFormatter.to_project_sarif(summary))

    assert document["runs"][0]["properties"]["verdict"] == "NEEDS_REVIEW"
    notifications = document["runs"][0]["invocations"][0]["toolExecutionNotifications"]
    assert notifications[0]["message"]["text"] == "Unable to read staged file"
