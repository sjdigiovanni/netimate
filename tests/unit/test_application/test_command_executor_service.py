# SPDX-License-Identifier: MPL-2.0
from unittest.mock import MagicMock

import pytest

from netimate.application.command_executor_service import CommandExecutorService


@pytest.mark.asyncio
async def test_run_valid_command(
    temp_device_and_settings_files,
    mock_runner,
    mock_registry,
    mock_settings,
    mock_template_provider,
):
    devices, _, _ = temp_device_and_settings_files
    mock_command = MagicMock()
    mock_registry.get_device_repository.return_value = MagicMock(
        return_value=MagicMock(list_devices=MagicMock(return_value=devices))
    )
    mock_registry.get_device_command.return_value = MagicMock(return_value=mock_command)
    mock_runner.run.return_value = [
        {"device": "r1", "result": "ok"},
        {"device": "r2", "result": "ok"},
    ]

    svc = CommandExecutorService(mock_registry, mock_settings, mock_template_provider, mock_runner)
    result = await svc.run(["r1", "r2"], "some-command")

    assert result == {"r1": "ok", "r2": "ok"}


@pytest.mark.asyncio
async def test_run_with_missing_device(
    temp_device_and_settings_files,
    mock_runner,
    mock_registry,
    mock_settings,
    mock_template_provider,
):
    devices, _, _ = temp_device_and_settings_files
    mock_registry.get_device_repository.return_value = MagicMock(
        return_value=MagicMock(list_devices=MagicMock(return_value=devices))
    )
    svc = CommandExecutorService(mock_registry, mock_settings, mock_template_provider, mock_runner)

    with pytest.raises(ValueError):
        await svc.run(["r1", "does-not-exist"], "some-command")
