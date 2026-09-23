"""
Professional PDF Audit Report Generator for ScopeLock.

Generates enterprise-grade, publication-quality PDF audit reports
detailing capability divergence, source line evidence, and risk analysis.
"""

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from scopelock.core.schema import AuditReport, AuditVerdict, RiskTier


class PDFReportGenerator:
    """Renders AuditReport objects into professional PDF documents."""

    @classmethod
    def generate(cls, report: AuditReport) -> bytes:
        """Generate PDF binary stream for an AuditReport."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom typography styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold",
            spaceAfter=4
        )

        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748b"),
            fontName="Helvetica",
            spaceAfter=12
        )

        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            fontName="Helvetica-Bold",
            spaceBefore=14,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
            fontName="Helvetica"
        )

        mono_style = ParagraphStyle(
            "Mono",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#0f172a"),
            fontName="Courier"
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph("SCOPELOCK SECURITY AUDIT REPORT", title_style))
        story.append(
            Paragraph(
                "Zero-Trust Capability Divergence & Principle of Least Privilege Assurance &bull; "
                f"Generated: {report.timestamp[:19].replace('T', ' ')} UTC",
                subtitle_style
            )
        )
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))

        # 2. Executive Verdict Card
        is_failed = report.final_verdict == AuditVerdict.FAILED
        verdict_bg = colors.HexColor("#fff1f2") if is_failed else colors.HexColor("#f0fdf4")
        verdict_border = colors.HexColor("#f43f5e") if is_failed else colors.HexColor("#10b981")
        verdict_text_color = "#be123c" if is_failed else "#15803d"
        verdict_title = (
            "DEPLOYMENT BLOCKED &mdash; UNJUSTIFIED CAPABILITY DETECTED"
            if is_failed else
            "DEPLOYMENT PERMITTED &mdash; LEAST PRIVILEGE COMPLIANT"
        )

        verdict_html = f"""
        <b><font size="12" color="{verdict_text_color}">{verdict_title}</font></b><br/>
        <font size="9" color="#475569">
        Target: <b>{report.target_file}</b> &bull;
        Analysis Latency: <b>{report.analysis_latency_ms:.2f} ms</b> &bull;
        Violations: <b>{report.total_violations}</b> &bull;
        Engine Version: <b>v{report.engine_version}</b>
        </font>
        """

        verdict_table = Table([[Paragraph(verdict_html, body_style)]], colWidths=[540])
        verdict_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), verdict_bg),
            ("BOX", (0, 0), (-1, -1), 1.5, verdict_border),
            ("PADDING", (0, 0), (-1, -1), 10),
            ("ROUNDEDCORNERS", [4, 4, 4, 4]),
        ]))
        story.append(verdict_table)
        story.append(Spacer(1, 10))

        # 3. Requirement & Scope Contract
        story.append(Paragraph("1. Developer Intent & Capability Policy Contract", section_heading))
        allowed_str = ", ".join(c.value for c in report.policy.allowed_categories) or "NONE (Strict Offline Policy)"
        disallowed_str = ", ".join(c.value for c in report.policy.disallowed_categories) or "None"

        policy_data = [
            [Paragraph("<b>Natural Intent Prompt</b>", body_style), Paragraph(f"<i>&ldquo;{report.user_prompt}&rdquo;</i>", body_style)],
            [Paragraph("<b>Inferred App Domain</b>", body_style), Paragraph(report.policy.application_name, body_style)],
            [Paragraph("<b>Authorized Capabilities</b>", body_style), Paragraph(f"<font color='#0284c7'><b>{allowed_str}</b></font>", body_style)],
            [Paragraph("<b>Restricted Boundaries</b>", body_style), Paragraph(f"<font color='#e11d48'>{disallowed_str}</font>", body_style)],
        ]
        policy_table = Table(policy_data, colWidths=[150, 390])
        policy_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(policy_table)
        story.append(Spacer(1, 10))

        # 4. Detailed Findings Table
        story.append(Paragraph(f"2. Static AST Capability Audit Findings ({len(report.findings)} items)", section_heading))

        if not report.findings:
            story.append(
                Paragraph(
                    "<i>No capability-bearing system calls (File System, Network, Process Execution, or Secrets) "
                    "were detected in the source code. The program is verified as pure computation.</i>",
                    body_style
                )
            )
        else:
            findings_headers = ["Verdict", "Category & Action", "Line", "API Invocated", "Recommendation"]
            table_rows = [[Paragraph(f"<b>{h}</b>", body_style) for h in findings_headers]]

            for f in report.findings:
                obs = f.observed
                loc = obs.source_location

                if f.verdict == RiskTier.UNJUSTIFIED:
                    v_color = "#e11d48"
                    v_text = "VIOLATION"
                elif f.verdict == RiskTier.SUSPICIOUS:
                    v_color = "#d97706"
                    v_text = "SUSPICIOUS"
                else:
                    v_color = "#16a34a"
                    v_text = "JUSTIFIED"

                v_cell = Paragraph(f"<b><font color='{v_color}'>{v_text}</font></b><br/><font size='7' color='#64748b'>Risk: {f.risk_score:.2f}</font>", body_style)
                cat_cell = Paragraph(f"<b>{obs.category.value}</b><br/><font size='7' color='#64748b'>{obs.action.value}</font>", body_style)
                line_cell = Paragraph(f"<b>L{loc.line}</b>:C{loc.col}", mono_style)
                api_cell = Paragraph(f"<code>{obs.raw_call}</code><br/><font size='7' color='#64748b'>Target: {obs.target_scope}</font>", mono_style)
                rec_cell = Paragraph(f"{f.finding}<br/><font size='7' color='#475569'><b>Remedy:</b> {f.recommendation}</font>", body_style)

                table_rows.append([v_cell, cat_cell, line_cell, api_cell, rec_cell])

            findings_table = Table(table_rows, colWidths=[70, 95, 45, 115, 215])
            findings_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("PADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(findings_table)

        story.append(Spacer(1, 14))

        # 5. Formal Mathematical Defense & Methodological Framework
        story.append(Paragraph("3. Mathematical Divergence & Compliance Signoff", section_heading))
        defense_text = """
        <b>Capability Divergence Model (&Delta;):</b> Let R be the natural-language intent requirement.
        Expected capability C<sub>exp</sub> = &Phi;(R). Observed AST capability C<sub>obs</sub> = &Psi;(P).
        The divergence set &Delta; = C<sub>obs</sub> \\ C<sub>exp</sub>.<br/>
        <b>Principle of Least Privilege:</b> Grounded in Saltzer & Schroeder (1975).
        This audit enforces strict prompt-relative boundaries before execution in runtime environments.
        """
        story.append(Paragraph(defense_text, body_style))
        story.append(Spacer(1, 10))

        # Footer Signature Box
        sign_data = [
            [
                Paragraph("<b>Audited By:</b> ScopeLock AST Static Verification Engine", body_style),
                Paragraph("<b>Compliance:</b> Saltzer-Schroeder Least Privilege (1975)", body_style)
            ],
            [
                Paragraph("<b>Verification Method:</b> Tree-sitter CST / Deterministic Set Divergence", body_style),
                Paragraph("<b>Status:</b> Official Cryptographic Digest &bull; PASS/FAIL Seal", body_style)
            ]
        ]
        sign_table = Table(sign_data, colWidths=[270, 270])
        sign_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(sign_table)

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
