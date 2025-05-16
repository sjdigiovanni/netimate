# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock, MagicMock

import pytest
import yaml

from netimate.application.application import Application
from netimate.interfaces.core.registry import PluginRegistryInterface
from netimate.interfaces.core.runner import RunnerInterface
from netimate.interfaces.infrastructure.settings import SettingsInterface
from netimate.interfaces.infrastructure.template_provider import TemplateProviderInterface
from netimate.models.device import Device


@pytest.fixture
def dummy_device():
    """Fixture providing a dummy telnet device for testing NetmikoTelnetConnectionProtocol."""
    return Device(
        name="test", host="10.1.1.1", username="u", password="p", protocol="telnet", platform="fake"
    )


@pytest.fixture
def temp_device_and_settings_files(tmp_path):
    """Fixture that creates a temp devices.yaml and settings.yaml file."""
    devices = [
        Device(
            name=f"r{i}",
            host=f"10.0.0.{i}",
            username="u",
            password="p",
            protocol="fake-async",
            platform="ios-xe",
            site=f"site{i}",
        )
        for i in range(1, 6)
    ]

    # Use the last device as a failing test
    devices[-1].protocol = "failing-async"

    temp_devices_path = tmp_path / "devices.yaml"
    temp_devices_path.write_text(yaml.safe_dump({"devices": [d.__dict__ for d in devices]}))

    settings_yaml = tmp_path / "settings.yaml"
    settings_yaml.write_text(
        f"plugin_configs:\n  yaml:\n    device_file: {temp_devices_path}\n"
        f"device_repo: yaml\n"
        f"log_level: 'off'\n"
        f"template_paths: 'test'\n"
    )

    return devices, temp_devices_path, settings_yaml


@pytest.fixture
def app_with_mock_command_repo_registry(temp_device_and_settings_files):
    devices, _, _ = temp_device_and_settings_files

    # Mock runner to simulate async execution
    mock_runner = AsyncMock()
    mock_runner.run.return_value = [
        {"device": d.name, "result": {"raw": "echo test"}} for d in devices
    ]

    # Mock command with fixed name and behavior
    mock_command = MagicMock()
    mock_command_instance = MagicMock()
    mock_command_instance.command_string.return_value = "echo test"
    mock_command.return_value = mock_command_instance
    mock_command.plugin_name = "echo-test"

    # Mock repository
    mock_repo = MagicMock()
    mock_repo.list_devices.return_value = devices
    mock_repo.plugin_name = "dummy"

    # Mock registry
    mock_registry = MagicMock()
    mock_registry.all_device_commands.return_value = {mock_command.plugin_name}
    mock_registry.all_device_repositories.return_value = {mock_repo.plugin_name}
    mock_registry.get_device_command.return_value = mock_command
    mock_registry.get_device_repository.return_value = lambda _: mock_repo
    mock_registry.get_protocol.return_value = lambda d: None

    # Construct minimal Application with mocks
    settings = MagicMock()
    settings.device_repo = "yaml"
    settings.device_file = "devices.yaml"

    return Application(
        settings=settings,
        registry=mock_registry,
        runner=mock_runner,
        template_provider=MagicMock(),
    )


@pytest.fixture
def fake_device():
    return Device(name="r1", site="siteA", os="ios", protocol="ssh")


@pytest.fixture
def fake_devices():
    return [
        Device(name="r1", site="siteA", os="ios", protocol="ssh"),
        Device(name="r2", site="siteA", os="ios", protocol="ssh"),
    ]


@pytest.fixture
def mock_registry():
    registry = MagicMock(spec=PluginRegistryInterface)
    return registry


@pytest.fixture
def mock_runner():
    return AsyncMock(spec=RunnerInterface)


@pytest.fixture
def mock_settings():
    settings = MagicMock(spec=SettingsInterface)
    settings.device_repo = "fake_repo"
    settings.plugin_configs = {}
    return settings


@pytest.fixture
def mock_template_provider():
    return MagicMock(spec=TemplateProviderInterface)

