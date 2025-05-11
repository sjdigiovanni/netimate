# SPDX-License-Identifier: MPL-2.0
import os
from pathlib import Path

import pytest

from netimate.composition import composition_root
from unittest.mock import MagicMock
from netimate.application.application import Application
from netimate.core.plugin_engine.plugin_registry import PluginRegistry


def test_list_usage(app_with_mock_command_repo_registry):
    result = app_with_mock_command_repo_registry.list("")
    assert "Usage" in result[0]


def test_list_device_repositories(app_with_mock_command_repo_registry):
    assert app_with_mock_command_repo_registry.list("device-repositories") == ["dummy"]


def test_list_device_commands(app_with_mock_command_repo_registry):
    assert app_with_mock_command_repo_registry.list("device-commands") == ["echo-test"]


def test_list_devices(app_with_mock_command_repo_registry):
    assert app_with_mock_command_repo_registry.list("devices") == ["r1", "r2", "r3", "r4", "r5"]


def test_list_snapshots_empty(app_with_mock_command_repo_registry):
    snapshots_dir = Path("snapshots")
    snapshots_dir.mkdir()

    try:
        result = app_with_mock_command_repo_registry.list("snapshots")
        assert result == ["[info] No snapshots found."]
    finally:
        if not any(snapshots_dir.iterdir()):
            snapshots_dir.rmdir()


def test_list_snapshots_found(app_with_mock_command_repo_registry):
    """Test that the application lists snapshot files if present."""
    snapshots_dir = Path("snapshots")
    snapshots_dir.mkdir(exist_ok=True)
    snapshot_file = snapshots_dir / "fake_snapshot.txt"
    snapshot_file.touch()

    try:
        result = app_with_mock_command_repo_registry.list("snapshots")
        assert "[1] fake_snapshot.txt" in result[0]
    finally:
        snapshot_file.unlink(missing_ok=True)
        if not any(snapshots_dir.iterdir()):
            snapshots_dir.rmdir()


def test_list_invalid(app_with_mock_command_repo_registry):
    result = app_with_mock_command_repo_registry.list("invalid-key")
    assert "[error]" in result[0]


@pytest.mark.asyncio
async def test_run_device_command(temp_device_and_settings_files):
    """Test that the application can run a command on a valid device."""
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files

    original_env = os.environ.get("NETIMATE_CONFIG_PATH")
    os.environ["NETIMATE_CONFIG_PATH"] = str(settings_yaml)
    os.environ["NETIMATE_EXTRA_PLUGIN_PACKAGES"] = "tests.fakes"

    try:
        app = composition_root()
        result = await app.run_device_command(["r1"], "echo-test")
        assert result == {"r1": {"raw": "echo test"}}
    finally:
        if original_env is not None:
            os.environ["NETIMATE_CONFIG_PATH"] = original_env
        else:
            os.environ.pop("NETIMATE_CONFIG_PATH", None)


@pytest.mark.asyncio
async def test_run_device_command_invalid_device(temp_device_and_settings_files):
    """Test that the application raises an error when the device provided is invalid."""
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files

    original_env = os.environ.get("NETIMATE_CONFIG_PATH")
    os.environ["NETIMATE_CONFIG_PATH"] = str(settings_yaml)

    try:
        app = composition_root()
        with pytest.raises(ValueError):
            await app.run_device_command(["invalid"], "echo-test")
    finally:
        if original_env is not None:
            os.environ["NETIMATE_CONFIG_PATH"] = original_env
        else:
            os.environ.pop("NETIMATE_CONFIG_PATH", None)


@pytest.mark.asyncio
async def test_device_not_found(app_with_mock_command_repo_registry):
    """
    Test that running a command on a nonexistent device raises a ValueError.
    """
    app = app_with_mock_command_repo_registry
    with pytest.raises(ValueError):
        await app.run_device_command(device_names=["x"], command_name="echo-test")


@pytest.mark.asyncio
async def test_bad_command():
    """
    Test that running a nonexistent command raises a KeyError, even when device and repo are valid.
    """
    app = Application(
        settings=MagicMock(),
        registry=PluginRegistry(),
        runner=MagicMock(),
        template_provider=MagicMock(),
    )

    with pytest.raises(KeyError):
        await app.run_device_command(device_names=["r1"], command_name="no-such-cmd")


def test_diff_snapshots(app_with_mock_command_repo_registry):
    snapshots_dir = Path("snapshots")
    snapshots_dir.mkdir(exist_ok=True)
    snapshot_file_1 = snapshots_dir / "R1_running_config_1.txt"
    snapshot_file_2 = snapshots_dir / "R1_running_config_2.txt"
    snapshot_file_1.write_text("interface Gig0/0\n ip address 1.1.1.1 255.255.255.0")
    snapshot_file_2.write_text("interface Gig0/0\n ip address 1.1.1.2 255.255.255.0")
    try:
        diff = app_with_mock_command_repo_registry.diff_snapshots("R1", 1, 2)
    finally:
        snapshot_file_1.unlink(missing_ok=True)
        snapshot_file_2.unlink(missing_ok=True)
        if not any(snapshots_dir.iterdir()):
            snapshots_dir.rmdir()

    assert "1.1.1.1" in diff
    assert "1.1.1.2" in diff
    assert "--- R1_running_config_1.txt" in diff
    assert "+++ R1_running_config_2.txt" in diff


def test_expand_device_names_expands_sites(app_with_mock_command_repo_registry):

    expanded = app_with_mock_command_repo_registry.expand_device_names(["site1"])
    assert sorted(expanded) == ["r1"]

    expanded = app_with_mock_command_repo_registry.expand_device_names(["r3"])
    assert expanded == ["r3"]

    expanded = app_with_mock_command_repo_registry.expand_device_names(["site2", "r1"])
    assert sorted(expanded) == ["r1", "r2"]
