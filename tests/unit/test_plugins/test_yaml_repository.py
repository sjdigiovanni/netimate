# SPDX-License-Identifier: MPL-2.0
from netimate.infrastructure.settings import SettingsImpl
from netimate.plugins.device_repositories.yaml import YamlDeviceRepository
import yaml


def test_yaml_repository_list_devices(temp_device_and_settings_files):
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files
    config = yaml.safe_load(settings_yaml.read_text())
    settings = SettingsImpl(
        device_repo=config.get("device_repo"),
        log_level=config.get("log_level"),
        template_paths=config.get("template_paths"),
        plugin_configs=config.get("plugin_configs"),
    )
    repo = YamlDeviceRepository(settings.plugin_configs.get("yaml"))
    devices = repo.list_devices()

    assert len(devices) == 5
    assert devices[0].name == "r1"
    assert devices[1].protocol == "fake-async"
