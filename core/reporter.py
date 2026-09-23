"""
Audit Report Generator for ScopeLock.

Formats security findings for terminal output, JSON exports,
and GitHub SARIF (Static Analysis Results Interchange Format).
"""

import json
from colorama import Fore, Style, init

from scopelock.core.schema import AuditReport, RiskTier, AuditVerdict

# Initialize colorama
init(autoreset=True)


class ReportFormatter:
    """Multi-format audit report serializer."""

    @classmethod
    def to_terminal(cls, report: AuditReport) -> str:
        """Render a high-impact terminal audit report."""
        lines = []
        width = 65
        lines.append(Fore.CYAN + "=" * width)
        lines.append(Fore.CYAN + Style.BRIGHT + " SCOPELOCK: CAPABILITY DIVERGENCE AUDIT REPORT ".center(width))
        lines.append(Fore.CYAN + "=" * width + Style.RESET_ALL)

        lines.append(f"{Style.BRIGHT}Target File   :{Style.RESET_ALL} {report.target_file}")
        lines.append(f"{Style.BRIGHT}Stated Intent :{Style.RESET_ALL} {report.user_prompt}")
        allowed = ", ".join(c.value for c in report.policy.allowed_categories) or "NONE (Offline Strict)"
        lines.append(f"{Style.BRIGHT}Allowed Scope :{Style.RESET_ALL} {allowed}")
        lines.append(f"{Style.BRIGHT}Latency       :{Style.RESET_ALL} {report.analysis_latency_ms:.2f} ms")
        lines.append("-" * width)

        if not report.findings:
            lines.append(Fore.GREEN + "  [CLEAN] No capability-bearing API calls detected." + Style.RESET_ALL)
        else:
            for idx, finding in enumerate(report.findings, start=1):
                obs = finding.observed
                loc = obs.source_location

                if finding.verdict == RiskTier.UNJUSTIFIED:
                    tag = Fore.RED + Style.BRIGHT + "[CRITICAL OVER-REACH]"
                    icon_color = Fore.RED
                elif finding.verdict == RiskTier.SUSPICIOUS:
                    tag = Fore.YELLOW + Style.BRIGHT + "[SUSPICIOUS DIVERGENCE]"
                    icon_color = Fore.YELLOW
                elif finding.verdict == RiskTier.JUSTIFIED:
                    tag = Fore.GREEN + Style.BRIGHT + "[AUTHORIZED]"
                    icon_color = Fore.GREEN
                else:
                    tag = Fore.MAGENTA + Style.BRIGHT + "[AMBIGUOUS INTENT]"
                    icon_color = Fore.MAGENTA

                lines.append(f"\n{tag} Finding #{idx}:{Style.RESET_ALL}")
                lines.append(f"  {icon_color}* Category      :{Style.RESET_ALL} {obs.category.value} -> {obs.action.value}")
                lines.append(f"  {icon_color}* API Invocated :{Style.RESET_ALL} {obs.raw_call}")
                lines.append(f"  {icon_color}* Source Target :{Style.RESET_ALL} {obs.target_scope}")
                lines.append(f"  {icon_color}* Location      :{Style.RESET_ALL} Line {loc.line}, Col {loc.col} in {loc.file}")
                if loc.snippet:
                    lines.append(f"  {icon_color}* Snippet       :{Style.RESET_ALL} {loc.snippet}")
                lines.append(f"  {icon_color}* Assessment    :{Style.RESET_ALL} {finding.finding}")
                lines.append(f"  {icon_color}* Recommendation:{Style.RESET_ALL} {finding.recommendation}")

        lines.append("\n" + "=" * width)
        if report.final_verdict == AuditVerdict.PASSED:
            verdict_str = Fore.GREEN + Style.BRIGHT + "[PASSED - LEAST PRIVILEGE PRESERVED]"
        elif report.final_verdict == AuditVerdict.FAILED:
            verdict_str = Fore.RED + Style.BRIGHT + f"[FAILED - {report.total_violations} UNJUSTIFIED CAPABILITY VIOLATIONS]"
        else:
            verdict_str = Fore.YELLOW + Style.BRIGHT + "[NEEDS REVIEW - AMBIGUOUS INTENT]"

        lines.append(f" Final Audit Verdict: {verdict_str}{Style.RESET_ALL}")
        lines.append("=" * width)
        return "\n".join(lines)

    @classmethod
    def to_json(cls, report: AuditReport) -> str:
        """Export report to standard indented JSON."""
        return report.model_dump_json(indent=2)

    @classmethod
    def to_sarif(cls, report: AuditReport) -> str:
        """Export report to SARIF format for GitHub Security integration."""
        sarif_results = []
        for finding in report.findings:
            if finding.verdict in (RiskTier.UNJUSTIFIED, RiskTier.SUSPICIOUS):
                loc = finding.observed.source_location
                sarif_results.append({
                    "ruleId": f"SCOPELOCK_{finding.observed.category.value}",
                    "level": "error" if finding.verdict == RiskTier.UNJUSTIFIED else "warning",
                    "message": {
                        "text": finding.finding
                    },
                    "locations": [{
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": loc.file
                            },
                            "region": {
                                "startLine": loc.line,
                                "startColumn": loc.col + 1
                            }
                        }
                    }]
                })

        sarif_doc = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "ScopeLock",
                        "semanticVersion": report.engine_version,
                        "informationUri": "https://github.com/ripplenexus/scopelock"
                    }
                },
                "results": sarif_results
            }]
        }
        return json.dumps(sarif_doc, indent=2)
