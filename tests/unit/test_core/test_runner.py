# SPDX-License-Identifier: MPL-2.0
import pytest


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
