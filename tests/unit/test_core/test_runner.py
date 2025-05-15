# SPDX-License-Identifier: MPL-2.0
from unittest.mock import MagicMock

import pytest

from netimate.core.plugin_engine.plugin_registry import PluginRegistry
from netimate.core.runner import Runner
from tests.fakes.fake_async_error import FailingAsyncProtocol


@pytest.mark.asyncio
async def test_runner_parallel_execution_unit(
    temp_device_and_settings_files, app_with_mock_command_repo_registry
):
    devices, _, _ = temp_device_and_settings_files

    # Run and assert
    results = await app_with_mock_command_repo_registry.run_device_command(
        [d.name for d in devices], "echo-test"
    )
    assert len(results) == 5
    for device in devices:
        assert results[device.name] == {"raw": "echo test"}


@pytest.mark.asyncio
async def test_runner_handles_device_error(temp_device_and_settings_files):
    """
    Ensure Runner returns a structured error when the protocol's connect()
    raises AuthError for a device.
    """

    devices, *_ = temp_device_and_settings_files
    device = [devices[-1]]

    registry = PluginRegistry()
    registry.register_protocol("failing-async", FailingAsyncProtocol)

    # Mock command with fixed name and behavior
    mock_command = MagicMock()
    mock_command_instance = MagicMock()
    mock_command_instance.command_string.return_value = "echo test"
    mock_command.return_value = mock_command_instance
    mock_command.plugin_name = "echo-test"

    runner = Runner(registry=registry, plugin_configs={})

    results = await runner.run(device, mock_command)
    result = results[0]

    assert result["success"] is False
    assert result["device"] == "r5"
    assert result["result"] == "bad creds"
    assert result["error"] == "bad creds"
    assert result["error_type"] == "AuthError"
