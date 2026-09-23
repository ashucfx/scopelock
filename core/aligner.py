"""
Zero-Trust Capability Alignment Engine for ScopeLock.

Computes the set-theoretic difference between observed program authority
and declared prompt requirements: Δ = C_obs \\ C_exp.
"""

from typing import List
from scopelock.core.schema import (
    ScopePolicy,
    ObservedCapability,
    DivergenceFinding,
    RiskTier,
    AuditVerdict,
    AuditReport,
)
from scopelock.core.taxonomy import CapabilityCategory


class CapabilityAligner:
    """Evaluates whether detected capabilities are justified by user intent."""

    @classmethod
    def align(
        cls,
        policy: ScopePolicy,
        observed_caps: List[ObservedCapability],
        target_file: str = "snippet.js",
        latency_ms: float = 0.0
    ) -> AuditReport:
        """
        Compare observed capabilities against the policy contract.
        """
        findings: List[DivergenceFinding] = []

        # If the intent itself is ambiguous, flag review required
        if policy.is_ambiguous:
            for obs in observed_caps:
                finding = DivergenceFinding(
                    observed=obs,
                    verdict=RiskTier.AMBIGUOUS,
                    risk_score=0.50,
                    finding=f"Capability {obs.category} cannot be verified because requirement intent is ambiguous.",
                    recommendation="Clarify developer requirements before accepting code."
                )
                findings.append(finding)

            return AuditReport(
                target_file=target_file,
                user_prompt=policy.stated_intent,
                policy=policy,
                findings=findings,
                total_violations=len(findings),
                final_verdict=AuditVerdict.NEEDS_REVIEW,
                analysis_latency_ms=latency_ms
            )

        # Standard alignment logic: Check each observed capability
        for obs in observed_caps:
            is_allowed = obs.category in policy.allowed_categories

            if not is_allowed:
                # UNJUSTIFIED VIOLATION
                score = 0.95 if obs.category in (
                    CapabilityCategory.PROCESS,
                    CapabilityCategory.SECRET,
                    CapabilityCategory.NETWORK
                ) else 0.75

                finding = DivergenceFinding(
                    observed=obs,
                    verdict=RiskTier.UNJUSTIFIED,
                    risk_score=score,
                    finding=(
                        f"Unjustified {obs.category.value} capability detected. "
                        f"The stated intent '{policy.stated_intent}' does not authorize "
                        f"invoking '{obs.raw_call}'."
                    ),
                    recommendation=(
                        f"Remove or refactor '{obs.raw_call}' at Line {obs.source_location.line}, "
                        f"Column {obs.source_location.col} before deploying to production."
                    )
                )
                findings.append(finding)
            else:
                # Allowed by category, verify scope if specified
                scope_match = True
                expected_match = None
                for exp in policy.expected_capabilities:
                    if exp.category == obs.category:
                        expected_match = exp
                        if exp.target_scope != "*" and obs.target_scope != "*":
                            if exp.target_scope not in obs.target_scope:
                                scope_match = False
                        break

                if scope_match:
                    finding = DivergenceFinding(
                        observed=obs,
                        verdict=RiskTier.JUSTIFIED,
                        risk_score=0.0,
                        finding=(
                            f"Justified {obs.category.value} access: "
                            f"'{obs.raw_call}' aligns with stated requirements."
                        ),
                        recommendation="Permission authorized by intent contract."
                    )
                else:
                    finding = DivergenceFinding(
                        observed=obs,
                        verdict=RiskTier.SUSPICIOUS,
                        risk_score=0.65,
                        finding=(
                            f"Capability {obs.category.value} is permitted, but target scope "
                            f"'{obs.target_scope}' exceeds declared target scope."
                        ),
                        recommendation="Audit destination endpoint or file path."
                    )
                findings.append(finding)

        # Calculate violations
        violations = [
            f for f in findings if f.verdict in (RiskTier.UNJUSTIFIED, RiskTier.SUSPICIOUS)
        ]
        final_verdict = AuditVerdict.FAILED if violations else AuditVerdict.PASSED

        return AuditReport(
            target_file=target_file,
            user_prompt=policy.stated_intent,
            policy=policy,
            findings=findings,
            total_violations=len(violations),
            final_verdict=final_verdict,
            analysis_latency_ms=latency_ms
        )
