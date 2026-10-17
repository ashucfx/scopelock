"""
ScopeLock Developer CLI.

Enterprise CLI for scanning AI-synthesized code against developer intent,
auditing entire repositories recursively, managing Git pre-commit hooks,
running empirical benchmarks, and serving the interactive security dashboard.
"""

import os
import subprocess
import sys
from pathlib import Path

import click
from colorama import Fore, Style, init

from scopelock import __version__
from scopelock.core.aligner import CapabilityAligner
from scopelock.core.intent_engine import IntentDecomposer
from scopelock.core.pdf_generator import PDFReportGenerator
from scopelock.core.project_scanner import PolicyConfigError, ProjectScanner
from scopelock.core.reporter import ReportFormatter
from scopelock.core.schema import AuditVerdict
from scopelock.scanner.engine import ScannerEngine

init(autoreset=True)


@click.group()
@click.version_option(version=__version__, message="%(prog)s v%(version)s")
def cli():
    """ScopeLock: Zero-Trust Security for AI-Generated Code."""


@cli.command()
@click.argument("file_path", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--prompt", "-p", required=True, help="Developer natural-language requirement prompt."
)
@click.option(
    "--json", "as_json", is_flag=True, help="Output structured JSON instead of terminal text."
)
@click.option("--sarif", "as_sarif", is_flag=True, help="Output OASIS SARIF format for CI/CD.")
def scan(file_path: str, prompt: str, as_json: bool, as_sarif: bool):
    """Scan a source file against the stated developer prompt intent."""
    scanner = ScannerEngine()
    caps, latency_ms, diagnostics = scanner.scan_file_detailed(file_path)

    policy = IntentDecomposer.decompose(prompt)
    report = CapabilityAligner.align(
        policy=policy,
        observed_caps=caps,
        target_file=file_path,
        latency_ms=latency_ms,
        diagnostics=diagnostics,
    )

    if as_json:
        click.echo(ReportFormatter.to_json(report))
    elif as_sarif:
        click.echo(ReportFormatter.to_sarif(report))
    else:
        click.echo(ReportFormatter.to_terminal(report))

    sys.exit(0 if report.final_verdict == AuditVerdict.PASSED else 1)


@cli.command(name="scan-project")
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--policy", "policy_file", help="Path to scopelock.json configuration policy.")
@click.option("--pdf", "pdf_output", help="Optional output path to save a PDF summary report.")
@click.option("--json", "as_json", is_flag=True, help="Output structured project JSON.")
@click.option("--sarif", "as_sarif", is_flag=True, help="Output aggregate SARIF for CI/CD.")
def scan_project(
    directory: str,
    policy_file: str | None,
    pdf_output: str | None,
    as_json: bool,
    as_sarif: bool,
):
    """
    Recursively audit an entire codebase directory.
    Automatically extracts in-code '// @intent: ...' comment headers.
    """
    # Machine-readable modes must emit exactly one document on stdout so callers
    # can pipe the output directly into JSON/SARIF consumers.
    if not (as_json or as_sarif):
        click.echo(Fore.CYAN + Style.BRIGHT + f"\n[SCAN] ScopeLock scanning project directory: {directory} ...")
    try:
        scanner = ProjectScanner(policy_file=policy_file)
    except (OSError, PolicyConfigError) as exc:
        click.echo(f"Invalid policy configuration: {exc}", err=True)
        sys.exit(2)
    summary = scanner.scan_directory(directory)

    if as_json:
        click.echo(ReportFormatter.to_project_json(summary))
        sys.exit(0 if summary.verdict == AuditVerdict.PASSED else 1)
    if as_sarif:
        click.echo(ReportFormatter.to_project_sarif(summary))
        sys.exit(0 if summary.verdict == AuditVerdict.PASSED else 1)

    click.echo("\n" + "=" * 70)
    click.echo(Fore.CYAN + Style.BRIGHT + " SCOPELOCK: PROJECT REPOSITORY AUDIT SUMMARY ".center(70))
    click.echo("=" * 70)
    click.echo(f"Total Files Scanned : {summary.scanned_files}")
    click.echo(f"Compliant Files     : {Fore.GREEN}{summary.clean_files}{Style.RESET_ALL}")
    click.echo(f"Over-privileged     : {Fore.RED if summary.violated_files > 0 else Fore.GREEN}{summary.violated_files}{Style.RESET_ALL}")
    click.echo(f"Needs Review        : {Fore.YELLOW}{summary.needs_review_files}{Style.RESET_ALL}")
    click.echo(f"Total Violations    : {summary.total_violations}")
    click.echo(f"Total AST Latency   : {summary.total_latency_ms:.2f} ms")
    click.echo("-" * 70)

    for report in summary.file_reports:
        if report.final_verdict == AuditVerdict.PASSED:
            status_tag = Fore.GREEN + "[PASS]"
        elif report.final_verdict == AuditVerdict.NEEDS_REVIEW:
            status_tag = Fore.YELLOW + "[REVIEW]"
        else:
            status_tag = Fore.RED + "[FAIL]"
        click.echo(f"{status_tag}{Style.RESET_ALL} {report.target_file:<40} ({report.policy.stated_intent[:25]}..)")

        for diagnostic in report.diagnostics:
            click.echo(f"    {Fore.YELLOW}* {diagnostic.severity}: {diagnostic.message}{Style.RESET_ALL}")

        for f in report.findings:
            if f.verdict != AuditVerdict.PASSED:
                loc = f.observed.source_location
                click.echo(f"    {Fore.RED}* L{loc.line}: {f.observed.category.value} -> {f.observed.raw_call} ({f.finding}){Style.RESET_ALL}")

    click.echo("=" * 70)

    # Export PDF if requested
    if pdf_output and summary.file_reports:
        pdf_bytes = PDFReportGenerator.generate(summary.file_reports[0])
        with open(pdf_output, "wb") as f:
            f.write(pdf_bytes)
        click.echo(Fore.GREEN + f"[PDF] Audit Report successfully saved to: {pdf_output}")

    if summary.verdict == AuditVerdict.FAILED:
        click.echo(Fore.RED + Style.BRIGHT + "\n[AUDIT FAILED] Capability over-reach detected. Deployment blocked.\n")
        sys.exit(1)
    if summary.verdict == AuditVerdict.NEEDS_REVIEW:
        click.echo(Fore.YELLOW + Style.BRIGHT + "\n[AUDIT NEEDS REVIEW] Scan errors or parser diagnostics prevent a clean result.\n")
        sys.exit(1)

    click.echo(Fore.GREEN + Style.BRIGHT + "\n[AUDIT PASSED] All repository modules comply with least-privilege intent.\n")
    sys.exit(0)


@cli.command(name="scan-staged")
@click.option("--policy", "policy_file", help="Path to scopelock.json configuration policy.")
@click.option("--json", "as_json", is_flag=True, help="Output structured project JSON.")
@click.option("--sarif", "as_sarif", is_flag=True, help="Output aggregate SARIF for CI/CD.")
def scan_staged(policy_file: str | None, as_json: bool, as_sarif: bool):
    """Audit supported source files as staged in the Git index."""
    try:
        scanner = ProjectScanner(policy_file=policy_file)
    except (OSError, ValueError) as exc:
        click.echo(f"Invalid policy configuration: {exc}", err=True)
        sys.exit(2)
    summary = scanner.scan_staged()
    if as_json:
        click.echo(ReportFormatter.to_project_json(summary))
    elif as_sarif:
        click.echo(ReportFormatter.to_project_sarif(summary))
    else:
        click.echo(f"Staged source files scanned: {summary.scanned_files}")
        click.echo(f"Violations: {summary.total_violations}")
        click.echo(f"Needs review: {summary.needs_review_files}")
        for error in summary.scan_errors:
            click.echo(f"[ERROR] {error}")
        for report in summary.file_reports:
            click.echo(f"[{report.final_verdict.value}] {report.target_file}")
            for diagnostic in report.diagnostics:
                click.echo(f"  [ERROR] {diagnostic.message}")

    if summary.verdict != AuditVerdict.PASSED:
        sys.exit(1)


@cli.command(name="init-hooks")
def init_hooks():
    """Install automated Git pre-commit hook in the current repository."""
    try:
        repo_root = Path(
            subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
        configured_hooks = subprocess.run(
            ["git", "config", "--path", "--get", "core.hooksPath"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if configured_hooks.returncode == 0:
            hooks_dir = Path(configured_hooks.stdout.strip())
            if not hooks_dir.is_absolute():
                hooks_dir = repo_root / hooks_dir
        else:
            hooks_dir = Path(
                subprocess.run(
                    ["git", "rev-parse", "--path-format=absolute", "--git-path", "hooks"],
                    cwd=repo_root,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
            )
    except (OSError, subprocess.CalledProcessError):
        click.echo(Fore.RED + "Error: Current directory is not inside a Git repository.")
        sys.exit(1)

    hooks_dir.mkdir(exist_ok=True)
    pre_commit_script = hooks_dir / "pre-commit"

    if pre_commit_script.exists():
        existing_content = pre_commit_script.read_text(encoding="utf-8", errors="replace")
        if "scopelock scan-staged" in existing_content:
            click.echo(Fore.GREEN + "ScopeLock staged audit hook is already installed.")
            return
        click.echo(
            Fore.RED
            + "An existing pre-commit hook was found and left unchanged. Add `scopelock scan-staged` to it manually."
        )
        sys.exit(2)

    hook_content = """#!/bin/sh
# ScopeLock automated pre-commit security check
echo "[ScopeLock] Auditing staged source files..."
scopelock scan-staged
"""
    with open(pre_commit_script, "w", encoding="utf-8") as f:
        f.write(hook_content)
    if os.name != "nt":
        pre_commit_script.chmod(0o755)

    click.echo(Fore.GREEN + Style.BRIGHT + f"[OK] ScopeLock hook installed at {pre_commit_script}.")
    click.echo("Each commit checks only supported source files in the Git index.")


@cli.command(name="audit-code")
@click.option("--code", "-c", required=True, help="Source code string to evaluate.")
@click.option("--prompt", "-p", required=True, help="Stated requirement prompt.")
@click.option("--lang", "-l", default="js", help="Language: js or py (default: js).")
def audit_code(code: str, prompt: str, lang: str):
    """Directly audit a raw code snippet against an intent prompt."""
    file_name = f"snippet.{lang}"
    scanner = ScannerEngine()
    caps, latency_ms, diagnostics = scanner.scan_code_detailed(code, file_name=file_name)

    policy = IntentDecomposer.decompose(prompt)
    report = CapabilityAligner.align(
        policy=policy,
        observed_caps=caps,
        target_file=file_name,
        latency_ms=latency_ms,
        diagnostics=diagnostics,
    )
    click.echo(ReportFormatter.to_terminal(report))

    sys.exit(0 if report.final_verdict == AuditVerdict.PASSED else 1)


@cli.command()
def benchmark():
    """Execute the 25-Program Empirical Benchmark Suite."""
    from scopelock.benchmarks.runner import BenchmarkRunner

    runner = BenchmarkRunner()
    runner.run_all()


@cli.command()
@click.option("--host", default="127.0.0.1", help="Binding host address.")
@click.option("--port", default=8000, help="HTTP server port.")
def serve(host: str, port: int):
    """Launch the interactive ScopeLock DevSecOps Web Dashboard."""
    import uvicorn

    click.echo(
        Fore.CYAN + Style.BRIGHT + f"Starting ScopeLock Web Dashboard on http://{host}:{port} ..."
    )
    uvicorn.run("scopelock.ui.server:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    cli()
