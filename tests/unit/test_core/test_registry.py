# SPDX-License-Identifier: MPL-2.0
import pytest

from netimate.core.plugin_engine.plugin_registry import PluginKind, PluginRegistry
from netimate.errors import RegistryError


class DummyPlugin:
    @staticmethod
    def name() -> str:
        return "dummy"


def test_register_device_command():
    registry = PluginRegistry()
    registry.register(PluginKind.DEVICE_COMMAND, "dummy", DummyPlugin)
    assert registry.get_device_command("dummy") is DummyPlugin


def test_register_protocol():
    registry = PluginRegistry()
    registry.register(PluginKind.PROTOCOL, "dummy", DummyPlugin)
    assert registry.get_protocol("dummy") is DummyPlugin


def test_register_repository():
    registry = PluginRegistry()
    registry.register(PluginKind.REPOSITORY, "dummy", DummyPlugin)
    assert registry.get_device_repository("dummy") is DummyPlugin


def test_register_unknown_kind_raises():
    registry = PluginRegistry()
    with pytest.raises(ValueError):
        registry.register("not-a-kind", "dummy", DummyPlugin)  # type: ignore


def test_missing_plugin_raises_registry_error():
    registry = PluginRegistry()

    with pytest.raises(RegistryError, match=f"No device command plugin named 'dummy' is "
                                            f"registered."):
        registry.get_device_command("dummy")

    with pytest.raises(RegistryError, match="No connection protocol plugin named 'dummy'"):
        registry.get_protocol("dummy")

    with pytest.raises(RegistryError, match="No repository plugin named 'dummy'"):
        registry.get_device_repository("dummy")
