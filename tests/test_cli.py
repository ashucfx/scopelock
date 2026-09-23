"""Test suite for ScopeLock CLI and Benchmark Suite."""

from click.testing import CliRunner
from scopelock.benchmarks.runner import BenchmarkRunner
from scopelock.cli.main import cli


def test_cli_version():
    """Verify version command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "v1.0.0" in result.output


def test_cli_audit_code_blocks_violation():
    """CLI audit-code must exit with code 1 when capability divergence is detected."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "audit-code",
            "--code",
            "fetch('https://malicious.com');",
            "--prompt",
            "Build a local offline calculator",
        ],
    )
    assert result.exit_code == 1
    assert "FAILED" in result.output


def test_cli_audit_code_passes_clean():
    """CLI audit-code must exit with code 0 on clean code."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "audit-code",
            "--code",
            "function add(a, b) { return a + b; }",
            "--prompt",
            "Build a local arithmetic calculator",
        ],
    )
    assert result.exit_code == 0
    assert "PASSED" in result.output


def test_benchmark_suite_metrics():
    """Run full benchmark and assert 100% precision & recall."""
    runner = BenchmarkRunner()
    metrics = runner.run_all()
    assert metrics["accuracy"] == 100.0
    assert metrics["recall"] == 100.0
    assert metrics["precision"] == 100.0
    assert metrics["fp"] == 0
    assert metrics["fn"] == 0
