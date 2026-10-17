"""Test suite for ScopeLock CLI and Benchmark Suite."""

import json
import subprocess

from click.testing import CliRunner

from scopelock.benchmarks.runner import BenchmarkRunner
from scopelock.cli.main import cli


def test_init_hooks_installs_staged_audit_in_git_repository(tmp_path, monkeypatch):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(cli, ["init-hooks"])
    hook = tmp_path / ".git" / "hooks" / "pre-commit"

    assert result.exit_code == 0
    assert "scopelock scan-staged" in hook.read_text(encoding="utf-8")
    assert "scan-project ." not in hook.read_text(encoding="utf-8")


def test_init_hooks_preserves_existing_hook(tmp_path, monkeypatch):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    hook = tmp_path / ".git" / "hooks" / "pre-commit"
    hook.write_text("#!/bin/sh\necho existing\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(cli, ["init-hooks"])

    assert result.exit_code == 2
    assert hook.read_text(encoding="utf-8") == "#!/bin/sh\necho existing\n"


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


def test_cli_audit_code_fails_closed_on_syntax_error():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["audit-code", "--code", "const = ;", "--prompt", "Build a local calculator"],
    )

    assert result.exit_code == 1
    assert "NEEDS REVIEW" in result.output
    assert "Parser reported an error node" in result.output


def test_cli_scan_project_fails_closed_on_syntax_error(tmp_path):
    (tmp_path / "broken.js").write_text("const = ;", encoding="utf-8")
    runner = CliRunner()

    result = runner.invoke(cli, ["scan-project", str(tmp_path)])

    assert result.exit_code == 1
    assert "AUDIT NEEDS REVIEW" in result.output


def test_cli_scan_file_fails_closed_on_syntax_error(tmp_path):
    source = tmp_path / "broken.js"
    source.write_text("const = ;", encoding="utf-8")

    result = CliRunner().invoke(
        cli, ["scan", str(source), "--prompt", "Build a local calculator"]
    )

    assert result.exit_code == 1
    assert "NEEDS REVIEW" in result.output
    assert "Parser reported an error node" in result.output


def test_cli_scan_sarif_includes_parser_diagnostics(tmp_path):
    source = tmp_path / "broken.js"
    source.write_text("const = ;", encoding="utf-8")

    result = CliRunner().invoke(
        cli,
        ["scan", str(source), "--prompt", "Build a local calculator", "--sarif"],
    )
    document = json.loads(result.output)

    assert result.exit_code == 1
    invocation = document["runs"][0]["invocations"][0]
    assert invocation["executionSuccessful"] is True
    assert invocation["toolExecutionNotifications"]


def test_benchmark_suite_metrics():
    """Run full benchmark and assert 100% precision & recall."""
    runner = BenchmarkRunner()
    metrics = runner.run_all()
    assert metrics["accuracy"] == 100.0
    assert metrics["recall"] == 100.0
    assert metrics["precision"] == 100.0
    assert metrics["fp"] == 0
    assert metrics["fn"] == 0


def test_cli_scan_project_rejects_invalid_policy(tmp_path):
    policy_file = tmp_path / "scopelock.json"
    policy_file.write_text("{invalid", encoding="utf-8")

    result = CliRunner().invoke(
        cli, ["scan-project", str(tmp_path), "--policy", str(policy_file), "--json"]
    )

    assert result.exit_code == 2
    assert "Invalid policy configuration" in result.stderr
