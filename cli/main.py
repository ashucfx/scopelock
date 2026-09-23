"""
ScopeLock Developer CLI.

Enterprise CLI for scanning AI-synthesized code against developer intent,
auditing entire repositories recursively, managing Git pre-commit hooks,
running empirical benchmarks, and serving the interactive security dashboard.
"""

import sys
from pathlib import Path

import click
from colorama import Fore, Style, init

from scopelock import __version__
from scopelock.core.aligner import CapabilityAligner
from scopelock.core.intent_engine import IntentDecomposer
from scopelock.core.pdf_generator import PDFReportGenerator
from scopelock.core.project_scanner import ProjectScanner
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
    caps, latency_ms = scanner.scan_file(file_path)

    policy = IntentDecomposer.decompose(prompt)
    report = CapabilityAligner.align(
        policy=policy, observed_caps=caps, target_file=file_path, latency_ms=latency_ms
    )

    if as_json:
        click.echo(ReportFormatter.to_json(report))
    elif as_sarif:
        click.echo(ReportFormatter.to_sarif(report))
    else:
        click.echo(ReportFormatter.to_terminal(report))

    if report.final_verdict == AuditVerdict.FAILED:
        sys.exit(1)
    sys.exit(0)


@cli.command(name="scan-project")
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--policy", "policy_file", help="Path to scopelock.json configuration policy.")
@click.option("--pdf", "pdf_output", help="Optional output path to save a PDF summary report.")
def scan_project(directory: str, policy_file: str | None, pdf_output: str | None):
    """
    Recursively audit an entire codebase directory.
    Automatically extracts in-code '// @intent: ...' comment headers.
    """
    click.echo(Fore.CYAN + Style.BRIGHT + f"\n[SCAN] ScopeLock scanning project directory: {directory} ...")
    scanner = ProjectScanner(policy_file=policy_file)
    summary = scanner.scan_directory(directory)

    click.echo("\n" + "=" * 70)
    click.echo(Fore.CYAN + Style.BRIGHT + " SCOPELOCK: PROJECT REPOSITORY AUDIT SUMMARY ".center(70))
    click.echo("=" * 70)
    click.echo(f"Total Files Scanned : {summary.scanned_files}")
    click.echo(f"Compliant Files     : {Fore.GREEN}{summary.clean_files}{Style.RESET_ALL}")
    click.echo(f"Over-privileged     : {Fore.RED if summary.violated_files > 0 else Fore.GREEN}{summary.violated_files}{Style.RESET_ALL}")
    click.echo(f"Total Violations    : {summary.total_violations}")
    click.echo(f"Total AST Latency   : {summary.total_latency_ms:.2f} ms")
    click.echo("-" * 70)

    for report in summary.file_reports:
        status_tag = Fore.GREEN + "[PASS]" if report.final_verdict == AuditVerdict.PASSED else Fore.RED + "[FAIL]"
        click.echo(f"{status_tag}{Style.RESET_ALL} {report.target_file:<40} ({report.policy.stated_intent[:25]}..)")

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

    click.echo(Fore.GREEN + Style.BRIGHT + "\n[AUDIT PASSED] All repository modules comply with least-privilege intent.\n")
    sys.exit(0)


@cli.command(name="init-hooks")
def init_hooks():
    """Install automated Git pre-commit hook in the current repository."""
    git_dir = Path(".git")
    if not git_dir.exists() or not git_dir.is_dir():
        click.echo(Fore.RED + "Error: Current directory is not a Git repository root.")
        sys.exit(1)

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    pre_commit_script = hooks_dir / "pre-commit"

    hook_content = """#!/bin/sh
# ScopeLock automated pre-commit security check
echo "[ScopeLock] Running Zero-Trust Capability Audit..."
scopelock scan-project .
if [ $? -ne 0 ]; then
    echo "[ScopeLock] Commit rejected: Unjustified capabilities detected in staged files."
    exit 1
fi
"""
    with open(pre_commit_script, "w", encoding="utf-8") as f:
        f.write(hook_content)

    click.echo(Fore.GREEN + Style.BRIGHT + "[OK] ScopeLock Git pre-commit hook installed successfully in .git/hooks/pre-commit!")
    click.echo("Every 'git commit' will now automatically verify code against least privilege before committing.")


@cli.command(name="audit-code")
@click.option("--code", "-c", required=True, help="Source code string to evaluate.")
@click.option("--prompt", "-p", required=True, help="Stated requirement prompt.")
@click.option("--lang", "-l", default="js", help="Language: js or py (default: js).")
def audit_code(code: str, prompt: str, lang: str):
    """Directly audit a raw code snippet against an intent prompt."""
    file_name = f"snippet.{lang}"
    scanner = ScannerEngine()
    caps, latency_ms = scanner.scan_code(code, file_name=file_name)

    policy = IntentDecomposer.decompose(prompt)
    report = CapabilityAligner.align(
        policy=policy, observed_caps=caps, target_file=file_name, latency_ms=latency_ms
    )
    click.echo(ReportFormatter.to_terminal(report))

    if report.final_verdict == AuditVerdict.FAILED:
        sys.exit(1)
    sys.exit(0)


@cli.command()
def benchmark():
    """Execute the 25-Program Empirical Benchmark Suite from the research paper."""
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
