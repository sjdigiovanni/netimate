# SPDX-License-Identifier: MPL-2.0
import subprocess
import sys
import os
import datetime
import pytest

from pathlib import Path
from unittest import mock

from netimate.application.application import Application


def test_shell_run_invalid_command(temp_device_and_settings_files):
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files
    env = os.environ.copy()
    env["NETIMATE_CONFIG_PATH"] = str(settings_yaml)

    result = subprocess.run(
        [sys.executable, "-m", "netimate", "--shell"],
        input="run invalid-command on r1\nexit\n",
        text=True,
        capture_output=True,
        env=env,
    )

    assert "Fatal" in result.stdout


def test_shell_list_commands_missing_key(temp_device_and_settings_files):
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files
    env = os.environ.copy()
    env["NETIMATE_CONFIG_PATH"] = str(settings_yaml)

    result = subprocess.run(
        [sys.executable, "-m", "netimate", "--shell"],
        input="list \nexit\n",
        text=True,
        capture_output=True,
        env=env,
    )

    assert (
        "Usage: list <devices [site] | device-repositories |"
        " device-commands | snapshots | sites>"
    ) in result.stdout


def test_shell_list_commands(temp_device_and_settings_files):
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files
    env = os.environ.copy()
    env["NETIMATE_CONFIG_PATH"] = str(settings_yaml)

    result = subprocess.run(
        [sys.executable, "-m", "netimate", "--shell"],
        input="list device-commands\nlist snapshots\nexit\n",
        text=True,
        capture_output=True,
        env=env,
    )

    assert "echo-test" in result.stdout
    assert "show-version" in result.stdout
    assert "snapshots" in result.stdout or "No snapshots directory found" in result.stdout


def test_shell_run_valid_command(temp_device_and_settings_files):
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files
    env = os.environ.copy()
    env["NETIMATE_CONFIG_PATH"] = str(settings_yaml)
    env["NETIMATE_EXTRA_PLUGIN_PACKAGES"] = "tests.fakes"

    result = subprocess.run(
        [sys.executable, "-m", "netimate", "--shell"],
        input="run echo-test on r1\nexit\n",
        text=True,
        capture_output=True,
        env=env,
    )

    assert "echo test" in result.stdout


def test_shell_log_level(temp_device_and_settings_files):
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files
    env = os.environ.copy()
    env["NETIMATE_CONFIG_PATH"] = str(settings_yaml)
    env["NETIMATE_EXTRA_PLUGIN_PACKAGES"] = "tests.fakes"

    result = subprocess.run(
        [sys.executable, "-m", "netimate", "--shell"],
        input="log_level info\nexit\n",
        text=True,
        capture_output=True,
        env=env,
    )

    assert "Switched log level to info" in result.stdout


def test_shell_log_level_invalid(temp_device_and_settings_files):
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files
    env = os.environ.copy()
    env["NETIMATE_CONFIG_PATH"] = str(settings_yaml)
    env["NETIMATE_EXTRA_PLUGIN_PACKAGES"] = "tests.fakes"

    result = subprocess.run(
        [sys.executable, "-m", "netimate", "--shell"],
        input="log_level test\nexit\n",
        text=True,
        capture_output=True,
        env=env,
    )

    assert "Error setting log level:" in result.stdout


def test_shell_snapshot_command(temp_device_and_settings_files):
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files
    env = os.environ.copy()
    env["NETIMATE_CONFIG_PATH"] = str(settings_yaml)
    env["NETIMATE_EXTRA_PLUGIN_PACKAGES"] = "tests.fakes"

    fixed_time = datetime.datetime(2024, 1, 1, 12, 0, 0)
    with (
        mock.patch("netimate.application.application.datetime") as mock_datetime,
        mock.patch("netimate.application.application.Path.write_text"),
    ):
        mock_datetime.datetime.now.return_value = fixed_time
        mock_datetime.datetime.strftime = datetime.datetime.strftime

        result = subprocess.run(
            [sys.executable, "-m", "netimate", "--shell"],
            input="snapshot r1\nexit\n",
            text=True,
            capture_output=True,
            env=env,
        )

    assert "Snapshot saved" in result.stdout or "Saved snapshot" in result.stdout

    snapshot_path = Path("snapshots")
    if snapshot_path.exists() and snapshot_path.is_dir():
        for file in snapshot_path.iterdir():
            file.unlink()
        snapshot_path.rmdir()


def test_shell_diagnostic_command(temp_device_and_settings_files):
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files
    env = os.environ.copy()
    env["NETIMATE_CONFIG_PATH"] = str(settings_yaml)
    env["NETIMATE_EXTRA_PLUGIN_PACKAGES"] = "tests.fakes"

    result = subprocess.run(
        [sys.executable, "-m", "netimate", "--shell"],
        input="diagnostic d1\nexit\n",
        text=True,
        capture_output=True,
        env=env,
    )

    assert "Diagnostics on d1" in result.stdout


def test_shell_run_syntax_error(temp_device_and_settings_files):
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files
    env = os.environ.copy()
    env["NETIMATE_CONFIG_PATH"] = str(settings_yaml)
    env["NETIMATE_EXTRA_PLUGIN_PACKAGES"] = "tests.fakes"

    result = subprocess.run(
        [sys.executable, "-m", "netimate", "--shell"],
        input="run only-one-word\nexit\n",
        text=True,
        capture_output=True,
        env=env,
    )

    assert "Syntax error" in result.stdout


def test_shell_empty_run_command(temp_device_and_settings_files):
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files
    env = os.environ.copy()
    env["NETIMATE_CONFIG_PATH"] = str(settings_yaml)
    env["NETIMATE_EXTRA_PLUGIN_PACKAGES"] = "tests.fakes"

    result = subprocess.run(
        [sys.executable, "-m", "netimate", "--shell"],
        input="run \nexit\n",
        text=True,
        capture_output=True,
        env=env,
    )

    assert "Syntax error" in result.stdout


def test_shell_snapshot_no_args(temp_device_and_settings_files):
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files
    env = os.environ.copy()
    env["NETIMATE_CONFIG_PATH"] = str(settings_yaml)
    env["NETIMATE_EXTRA_PLUGIN_PACKAGES"] = "tests.fakes"

    result = subprocess.run(
        [sys.executable, "-m", "netimate", "--shell"],
        input="snapshot\nexit\n",
        text=True,
        capture_output=True,
        env=env,
    )

    assert "Usage: snapshot <device1>" in result.stdout


def test_shell_diagnostic_no_args(temp_device_and_settings_files):
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files
    env = os.environ.copy()
    env["NETIMATE_CONFIG_PATH"] = str(settings_yaml)
    env["NETIMATE_EXTRA_PLUGIN_PACKAGES"] = "tests.fakes"

    result = subprocess.run(
        [sys.executable, "-m", "netimate", "--shell"],
        input="diagnostic\nexit\n",
        text=True,
        capture_output=True,
        env=env,
    )

    assert "Usage: diagnostic <device1>" in result.stdout


def test_shell_diagnostic_prints_summary(capsys):
    fake_outputs = {"r1": {"show-version": [{}]}}
    from netimate.view.shell.shell_session import netimateShellSession

    app_mock = mock.Mock()
    app_mock.diagnostic = mock.AsyncMock(return_value=fake_outputs)
    cmd_mock = mock.Mock()
    cmd_mock.label = "show-version"
    cmd_mock.summarise_result.return_value = "Test Summary"
    app_mock.get_device_command.return_value = cmd_mock

    shell = netimateShellSession(app_mock)
    shell._cmd_diagnostic(["r1"])

    captured = capsys.readouterr()
    assert "Diagnostics on" in captured.out
    assert "show-version" in captured.out


def test_shell_diff_snapshots_command(temp_device_and_settings_files):
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files
    env = os.environ.copy()
    env["NETIMATE_CONFIG_PATH"] = str(settings_yaml)
    env["NETIMATE_EXTRA_PLUGIN_PACKAGES"] = "tests.fakes"

    fixed_time = datetime.datetime(2024, 1, 1, 12, 0, 0)

    with mock.patch("netimate.application.application.datetime") as mock_datetime:
        mock_datetime.datetime.now.return_value = fixed_time
        mock_datetime.datetime.strftime = datetime.datetime.strftime

        # Simulate snapshots
        snapshots_path = Path("snapshots")
        snapshots_path.mkdir(exist_ok=True)

        (snapshots_path / "R1_running_config_20240101-120000.txt").write_text(
            "interface Gig0/0\n ip address 1.1.1.1 255.255.255.0"
        )
        (snapshots_path / "R1_running_config_20240101-120100.txt").write_text(
            "interface Gig0/0\n ip address 1.1.1.2 255.255.255.0"
        )

        result = subprocess.run(
            [sys.executable, "-m", "netimate", "--shell"],
            input="diff_snapshots R1 1 2\nexit\n",
            text=True,
            capture_output=True,
            env=env,
        )

    stdout = result.stdout.lower()
    assert "interface gig0/0" in stdout
    assert "- ip address 1.1.1.1" in stdout
    assert "+ ip address 1.1.1.2" in stdout

    # Cleanup
    if snapshots_path.exists() and snapshots_path.is_dir():
        for file in snapshots_path.iterdir():
            file.unlink()
        snapshots_path.rmdir()


def test_shell_run_command_on_site(temp_device_and_settings_files):
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files
    env = os.environ.copy()
    env["NETIMATE_CONFIG_PATH"] = str(settings_yaml)
    env["NETIMATE_EXTRA_PLUGIN_PACKAGES"] = "tests.fakes"

    # Patch the time if snapshot timestamps are needed (skip for run)
    result = subprocess.run(
        [sys.executable, "-m", "netimate", "--shell"],
        input="run echo-test on site1\nexit\n",
        text=True,
        capture_output=True,
        env=env,
    )

    assert "Running 'echo-test'" in result.stdout
    assert "r1" in result.stdout or "r2" in result.stdout
