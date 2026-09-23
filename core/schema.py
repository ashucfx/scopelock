"""
Pydantic Schemas for ScopeLock Data Models.

Provides runtime type safety and strict schema validation for capabilities,
intent contracts, divergence findings, and audit reports.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Set
from pydantic import BaseModel, Field

from scopelock.core.taxonomy import CapabilityCategory, CapabilityAction


class RiskTier(str, Enum):
    """Categorical risk tiers for capability divergence."""
    JUSTIFIED = "JUSTIFIED"
    CONDITIONALLY_JUSTIFIED = "CONDITIONALLY_JUSTIFIED"
    SUSPICIOUS = "SUSPICIOUS"
    UNJUSTIFIED = "UNJUSTIFIED"
    AMBIGUOUS = "AMBIGUOUS"


class AuditVerdict(str, Enum):
    """Final pipeline deployment decision."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class SourceLocation(BaseModel):
    """Accurate source coordinate representation."""
    file: str = "snippet.js"
    line: int = Field(ge=1, description="1-indexed line number")
    col: int = Field(ge=0, description="0-indexed column number")
    end_line: Optional[int] = None
    end_col: Optional[int] = None
    snippet: Optional[str] = None


class ObservedCapability(BaseModel):
    """A capability extracted statically (AST) or dynamically (sandbox)."""
    category: CapabilityCategory
    action: CapabilityAction
    source_location: SourceLocation
    raw_call: str
    target_scope: Optional[str] = "*"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    origin: str = "STATIC_AST"


class ExpectedCapability(BaseModel):
    """An authorized capability derived from human intent."""
    category: CapabilityCategory
    action: Optional[str] = "*"
    target_scope: str = Field(default="*", description="Permitted domain/path pattern")
    justification: str = Field(description="Why this is authorized by intent")
    is_conditional: bool = False
    condition_description: Optional[str] = None


class ScopePolicy(BaseModel):
    """Formal Expected Capability Contract synthesized from developer prompt."""
    application_name: str = "TargetApp"
    stated_intent: str
    allowed_categories: Set[CapabilityCategory] = Field(default_factory=set)
    expected_capabilities: List[ExpectedCapability] = Field(default_factory=list)
    disallowed_categories: Set[CapabilityCategory] = Field(default_factory=set)
    is_ambiguous: bool = False
    clarification_prompt: Optional[str] = None


class DivergenceFinding(BaseModel):
    """Individual capability finding with evidence and recommendation."""
    observed: ObservedCapability
    verdict: RiskTier
    risk_score: float = Field(ge=0.0, le=1.0)
    finding: str
    recommendation: str


class AuditReport(BaseModel):
    """Final, comprehensive security audit report."""
    target_file: str
    user_prompt: str
    policy: ScopePolicy
    findings: List[DivergenceFinding] = Field(default_factory=list)
    total_violations: int = 0
    final_verdict: AuditVerdict = AuditVerdict.PASSED
    analysis_latency_ms: float = 0.0
    engine_version: str = "1.0.0"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def has_violations(self) -> bool:
        """Check if any finding is UNJUSTIFIED or SUSPICIOUS."""
        return any(f.verdict in (RiskTier.UNJUSTIFIED, RiskTier.SUSPICIOUS) for f in self.findings)
