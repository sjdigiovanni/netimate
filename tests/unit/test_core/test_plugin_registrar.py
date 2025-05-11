# SPDX-License-Identifier: MPL-2.0
from netimate.core.plugin_engine.registrar import PluginRegistrar
from netimate.core.plugin_engine.plugin_registry import PluginRegistry, PluginKind


class DummyCommand:
    @staticmethod
    def plugin_name() -> str:
        return "dummy-command"


class DummyLoader:
    def __init__(self, *args, **kwargs):
        pass

    def discover(self):
        return [DummyCommand]


def test_registers_command(monkeypatch):
    registry = PluginRegistry()
    registrar = PluginRegistrar(registry)

    # Patch PluginLoader used inside registrar to return DummyLoader instead
    monkeypatch.setattr(
        "netimate.core.plugin_engine.registrar.PluginLoader", lambda *args, **kwargs: DummyLoader()
    )

    registrar.register_plugins(PluginKind.DEVICE_COMMAND, "fake.path.device_commands", DummyCommand)

    assert "dummy-command" in registry.all_device_commands()
    assert registry.get_device_command("dummy-command") is DummyCommand
