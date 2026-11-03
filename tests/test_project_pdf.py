"""Tests for aggregate project PDF generation."""

from io import BytesIO

from pypdf import PdfReader

from scopelock.core.pdf_generator import PDFReportGenerator
from scopelock.core.project_scanner import ProjectAuditSummary


def test_project_pdf_contains_repository_summary():
    pdf = PDFReportGenerator.generate_project(ProjectAuditSummary(scanned_files=3))
    reader = PdfReader(BytesIO(pdf))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    assert "SCOPELOCK PROJECT SECURITY AUDIT" in text
    assert "Files scanned" in text
    assert "3" in text
