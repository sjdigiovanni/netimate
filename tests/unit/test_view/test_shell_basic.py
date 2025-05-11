# SPDX-License-Identifier: MPL-2.0
import pytest
from netimate.view.shell.shell_session import netimateShellSession as Shell


def test_shell_exit(capsys, app_with_mock_command_repo_registry):
    shell = Shell(app_with_mock_command_repo_registry)
    with pytest.raises(SystemExit) as excinfo:
        shell._dispatch("exit")
    assert excinfo.value.code == 0


def test_shell_invalid_list_usage(capsys, app_with_mock_command_repo_registry):
    shell = Shell(app_with_mock_command_repo_registry)
    shell._cmd_list([])
    captured = capsys.readouterr()
    assert "Usage: list" in captured.out


def test_shell_invalid_snapshot_usage(capsys, app_with_mock_command_repo_registry):
    shell = Shell(app_with_mock_command_repo_registry)
    shell._cmd_snapshot([])
    captured = capsys.readouterr()
    assert "Usage: snapshot" in captured.out


def test_shell_invalid_diagnostic_usage(capsys, app_with_mock_command_repo_registry):
    shell = Shell(app_with_mock_command_repo_registry)
    shell._cmd_diagnostic([])
    captured = capsys.readouterr()
    assert "Usage: diagnostic" in captured.out


def test_shell_invalid_diff_snapshots_usage(capsys, app_with_mock_command_repo_registry):
    shell = Shell(app_with_mock_command_repo_registry)
    shell._cmd_diff_snapshots([])
    captured = capsys.readouterr()
    assert "Usage: diff-snapshots" in captured.out


def test_shell_invalid_run_syntax(capsys, app_with_mock_command_repo_registry):
    shell = Shell(app_with_mock_command_repo_registry)
    with pytest.raises(ValueError):
        shell._cmd_run(["invalid", "syntax", "without", "on", "keyword"])


def test_shell_invalid_log_level(capsys, app_with_mock_command_repo_registry):
    shell = Shell(app_with_mock_command_repo_registry)
    shell._cmd_log_level(["INVALID_LEVEL"])
    captured = capsys.readouterr()
    assert "Error setting log level" in captured.out


def test_shell_diff_snapshots_error(capsys, app_with_mock_command_repo_registry, monkeypatch):
    shell = Shell(app_with_mock_command_repo_registry)

    # Force diff_snapshots to throw
    def raise_exception(*args, **kwargs):
        raise Exception("Forced error")

    monkeypatch.setattr(shell.app, "diff_snapshots", raise_exception)

    with pytest.raises(Exception):
        shell._cmd_diff_snapshots(["r1", "1", "2"])
