"""Test suite for Intent Decomposer and Alignment."""

import pytest
from scopelock.core.intent_engine import HeuristicIntentEngine, IntentDecomposer
from scopelock.core.taxonomy import CapabilityCategory
from scopelock.core.schema import AuditVerdict, RiskTier
from scopelock.core.aligner import CapabilityAligner
from scopelock.scanner.engine import ScannerEngine


def test_offline_calculator_intent():
    """Calculator requirement should authorize zero ambient capabilities."""
    policy = HeuristicIntentEngine.decompose("Build a local arithmetic calculator CLI")
    assert CapabilityCategory.NETWORK in policy.disallowed_categories
    assert CapabilityCategory.FILESYSTEM in policy.disallowed_categories
    assert CapabilityCategory.PROCESS in policy.disallowed_categories
    assert len(policy.allowed_categories) == 0


def test_ambiguous_intent_detection():
    """Vague prompt should be flagged as ambiguous."""
    policy = HeuristicIntentEngine.decompose("Build a tool to do whatever with my stuff")
    assert policy.is_ambiguous is True
    assert policy.clarification_prompt is not None


def test_alignment_catches_unauthorized_egress():
    """Calculator code with hidden fetch must fail audit with UNJUSTIFIED verdict."""
    prompt = "Build a local offline calculator"
    code = """
    function calculate(a, b) {
        fetch("https://analytics.tracker.com/log");
        return a + b;
    }
    """
    scanner = ScannerEngine()
    caps, lat = scanner.scan_code(code)
    policy = IntentDecomposer.decompose(prompt)
    report = CapabilityAligner.align(policy, caps, latency_ms=lat)

    assert report.final_verdict == AuditVerdict.FAILED
    assert report.total_violations == 1
    assert report.findings[0].verdict == RiskTier.UNJUSTIFIED
    assert report.findings[0].observed.category == CapabilityCategory.NETWORK


def test_alignment_passes_legitimate_code():
    """CSV parser with legitimate fs.readFileSync should pass audit."""
    prompt = "Read local CSV file and parse contents"
    code = """
    const fs = require('fs');
    const data = fs.readFileSync('dataset.csv', 'utf8');
    """
    scanner = ScannerEngine()
    caps, lat = scanner.scan_code(code)
    policy = IntentDecomposer.decompose(prompt)
    report = CapabilityAligner.align(policy, caps, latency_ms=lat)

    assert report.final_verdict == AuditVerdict.PASSED
    assert report.total_violations == 0
    assert report.findings[0].verdict == RiskTier.JUSTIFIED
