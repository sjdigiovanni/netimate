# SPDX-License-Identifier: MPL-2.0
import pytest

from netimate.core.plugin_engine.plugin_registry import PluginKind, PluginRegistry


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
