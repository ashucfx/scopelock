"""
ScopeLock Developer CLI.

Enterprise CLI for scanning AI-synthesized code against developer intent,
running empirical benchmarks, and serving the interactive security dashboard.
"""

import sys

import click
from colorama import Fore, Style, init

from scopelock import __version__
from scopelock.core.aligner import CapabilityAligner
from scopelock.core.intent_engine import IntentDecomposer
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

    # Exit code 1 if audit failed (blocks CI/CD pull request)
    if report.final_verdict == AuditVerdict.FAILED:
        sys.exit(1)
    sys.exit(0)


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
