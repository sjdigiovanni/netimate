# SPDX-License-Identifier: MPL-2.0
import sys

import pytest

from netimate.core.plugin_engine.loader import PluginLoader
from netimate.infrastructure.config_loader import ConfigLoader
from netimate.infrastructure.settings import SettingsImpl


def test_config_loader_minimal(temp_device_and_settings_files):
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files
    loader = ConfigLoader(str(settings_yaml))
    config = loader.load()
    assert isinstance(config, SettingsImpl)
    assert config.device_repo == "yaml"
    assert "devices.yaml" in config.plugin_configs.get("yaml").get("device_file")
    assert config.log_level == "off"


def test_config_loader_missing_file(tmp_path):
    missing_path = tmp_path / "does_not_exist.yaml"
    with pytest.raises(FileNotFoundError):
        ConfigLoader(str(missing_path))


def test_config_loader_missing_key(tmp_path):
    config_path = tmp_path / "bad.yaml"
    config_path.write_text("device_repo: yaml\ndevice_file: devices.yaml")
    loader = ConfigLoader(str(config_path))
    with pytest.raises(ValueError, match="Missing required config value"):
        loader.load()


def test_config_loader_empty_file(tmp_path):
    config_path = tmp_path / "empty.yaml"
    config_path.write_text("")
    loader = ConfigLoader(str(config_path))
    with pytest.raises(ValueError, match="Missing required config value"):
        loader.load()


# Test for ImportError handling in PluginLoader._scan_package (lines 23-25 in loader.py)
def test_plugin_loader_import_error(monkeypatch):

    def mock_import_module(name):
        raise ImportError("Mock import error")

    monkeypatch.setattr("importlib.import_module", mock_import_module)
    loader = PluginLoader(base_paths=["fake_package"], interface=object)
    # Should not raise (just logs warning and returns)
    loader._scan_package("fake_package", [])


# Test for Exception during submodule import (lines 38-40 in loader.py)
def test_plugin_loader_submodule_import_error(tmp_path, monkeypatch):
    # Create a fake module structure
    fake_package = tmp_path / "fake_package"
    fake_package.mkdir()
    (fake_package / "__init__.py").write_text("")
    (fake_package / "bad_module.py").write_text("raise Exception('Boom')")

    # Add tmp_path to sys.path so importlib can find it
    sys.path.insert(0, str(tmp_path))

    loader = PluginLoader(base_paths=["fake_package"], interface=object)
    discovered = []
    loader._scan_package("fake_package", discovered)

    # Cleanup sys.path
    sys.path.pop(0)
