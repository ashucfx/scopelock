"""Test suite for Intent Decomposer and Alignment."""

from scopelock.core.aligner import CapabilityAligner
from scopelock.core.intent_engine import HeuristicIntentEngine, IntentDecomposer
from scopelock.core.schema import (
    AuditVerdict,
    ExpectedCapability,
    ObservedCapability,
    RiskTier,
    ScopePolicy,
    SourceLocation,
)
from scopelock.core.taxonomy import CapabilityAction, CapabilityCategory
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


def test_alignment_enforces_action_and_target_scope():
    """A permitted category must not authorize unrelated actions or destinations."""
    policy = ScopePolicy(
        stated_intent="Fetch weather from the approved service",
        allowed_categories={CapabilityCategory.NETWORK},
        expected_capabilities=[
            ExpectedCapability(
                category=CapabilityCategory.NETWORK,
                action=CapabilityAction.NET_HTTP_GET.value,
                target_scope="api.weather.com/*",
                justification="The weather provider is required.",
            )
        ],
    )
    approved = ObservedCapability(
        category=CapabilityCategory.NETWORK,
        action=CapabilityAction.NET_HTTP_GET,
        source_location=SourceLocation(line=1, col=0),
        raw_call="fetch",
        target_scope="api.weather.com/current",
    )
    disallowed = ObservedCapability(
        category=CapabilityCategory.NETWORK,
        action=CapabilityAction.NET_HTTP_POST,
        source_location=SourceLocation(line=2, col=0),
        raw_call="fetch",
        target_scope="evil.example/exfiltrate",
    )

    report = CapabilityAligner.align(policy, [approved, disallowed])

    assert report.final_verdict == AuditVerdict.FAILED
    assert report.total_violations == 1
    assert report.findings[0].verdict == RiskTier.JUSTIFIED
    assert report.findings[1].verdict == RiskTier.UNJUSTIFIED


def test_database_intent_authorizes_database_capabilities():
    """Database requirements should authorize database access but not network access."""
    policy = HeuristicIntentEngine.decompose("Build a SQLite database query utility")

    assert CapabilityCategory.DATABASE in policy.allowed_categories
    assert CapabilityCategory.NETWORK in policy.disallowed_categories


def test_negated_network_capability_does_not_grant_permission():
    for prompt in (
        "Build a utility that does not use network access",
        "Build a utility with no API requests",
        "Build a utility without fetching data",
        "Build a utility; network access is forbidden",
    ):
        policy = HeuristicIntentEngine.decompose(prompt)
        assert CapabilityCategory.NETWORK not in policy.allowed_categories
        assert CapabilityCategory.NETWORK in policy.disallowed_categories


def test_explicit_positive_network_capability_still_grants_permission():
    policy = HeuristicIntentEngine.decompose("Fetch current weather from the weather API")

    assert CapabilityCategory.NETWORK in policy.allowed_categories
    assert CapabilityCategory.NETWORK not in policy.disallowed_categories
