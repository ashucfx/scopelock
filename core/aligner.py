"""
Zero-Trust Capability Alignment Engine for ScopeLock.

Computes the set-theoretic difference between observed program authority
and declared prompt requirements: Δ = C_obs \\ C_exp.
"""

from fnmatch import fnmatchcase

from scopelock.core.schema import (
    AuditReport,
    AuditVerdict,
    DivergenceFinding,
    ObservedCapability,
    RiskTier,
    ScanDiagnostic,
    ScopePolicy,
)
from scopelock.core.taxonomy import CapabilityCategory


class CapabilityAligner:
    """Evaluates whether detected capabilities are justified by user intent."""

    @classmethod
    def align(
        cls,
        policy: ScopePolicy,
        observed_caps: list[ObservedCapability],
        target_file: str = "snippet.js",
        latency_ms: float = 0.0,
        diagnostics: list[ScanDiagnostic] | None = None,
    ) -> AuditReport:
        """
        Compare observed capabilities against the policy contract.
        """
        findings: list[DivergenceFinding] = []
        diagnostics = diagnostics or []

        # If the intent itself is ambiguous, flag review required
        if policy.is_ambiguous:
            for obs in observed_caps:
                finding = DivergenceFinding(
                    observed=obs,
                    verdict=RiskTier.AMBIGUOUS,
                    risk_score=0.50,
                    finding=f"Capability {obs.category} cannot be verified because requirement intent is ambiguous.",
                    recommendation="Clarify developer requirements before accepting code.",
                )
                findings.append(finding)

            return AuditReport(
                target_file=target_file,
                user_prompt=policy.stated_intent,
                policy=policy,
                findings=findings,
                total_violations=len(findings),
                final_verdict=AuditVerdict.NEEDS_REVIEW,
                analysis_latency_ms=latency_ms,
                diagnostics=diagnostics,
            )

        # Standard alignment logic: Check each observed capability
        for obs in observed_caps:
            category_allowed = (
                obs.category in policy.allowed_categories
                and obs.category not in policy.disallowed_categories
            )
            is_allowed = cls._is_authorized(policy, obs)

            if not is_allowed:
                # A permitted category with an invalid action/scope is suspicious;
                # a denied category is an outright policy violation.
                verdict = RiskTier.SUSPICIOUS if category_allowed else RiskTier.UNJUSTIFIED
                score = (
                    0.65 if category_allowed else 0.95
                    if obs.category
                    in (
                        CapabilityCategory.PROCESS,
                        CapabilityCategory.SECRET,
                        CapabilityCategory.NETWORK,
                    )
                    else 0.75
                )

                finding = DivergenceFinding(
                    observed=obs,
                    verdict=verdict,
                    risk_score=score,
                    finding=(
                        f"{'Suspicious' if category_allowed else 'Unjustified'} "
                        f"{obs.category.value} capability detected. "
                        f"The stated intent '{policy.stated_intent}' does not authorize "
                        f"invoking '{obs.raw_call}'."
                    ),
                    recommendation=(
                        f"Remove or refactor '{obs.raw_call}' at Line {obs.source_location.line}, "
                        f"Column {obs.source_location.col} before deploying to production."
                    ),
                )
                findings.append(finding)
            else:
                # Allowed by category, verify scope if specified
                scope_match = True
                for exp in policy.expected_capabilities:
                    if exp.category == obs.category:
                        if (
                            exp.target_scope != "*"
                            and obs.target_scope != "*"
                            and exp.target_scope not in obs.target_scope
                        ):
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
                        recommendation="Permission authorized by intent contract.",
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
                        recommendation="Audit destination endpoint or file path.",
                    )
                findings.append(finding)

        # Calculate violations
        violations = [
            f for f in findings if f.verdict in (RiskTier.UNJUSTIFIED, RiskTier.SUSPICIOUS)
        ]
        if violations:
            final_verdict = AuditVerdict.FAILED
        elif any(d.severity.upper() == "ERROR" for d in diagnostics):
            final_verdict = AuditVerdict.NEEDS_REVIEW
        else:
            final_verdict = AuditVerdict.PASSED

        return AuditReport(
            target_file=target_file,
            user_prompt=policy.stated_intent,
            policy=policy,
            findings=findings,
            total_violations=len(violations),
            final_verdict=final_verdict,
            analysis_latency_ms=latency_ms,
            diagnostics=diagnostics,
        )

    @classmethod
    def _is_authorized(cls, policy: ScopePolicy, observed: ObservedCapability) -> bool:
        """Match a capability against category, action, and target scope policy."""
        if observed.category in policy.disallowed_categories:
            return False
        if observed.category not in policy.allowed_categories:
            return False

        expected = [
            item
            for item in policy.expected_capabilities
            if item.category == observed.category
        ]
        if not expected:
            return True

        for item in expected:
            action_matches = item.action in (None, "*", observed.action.value)
            scope_matches = item.target_scope in ("*", None) or (
                observed.target_scope not in (None, "*")
                and fnmatchcase(observed.target_scope, item.target_scope)
            )
            if action_matches and scope_matches:
                return True
        return False
