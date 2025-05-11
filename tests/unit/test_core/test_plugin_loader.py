# SPDX-License-Identifier: MPL-2.0
from netimate.core.plugin_engine.loader import PluginLoader
from netimate.interfaces.plugin.plugin import Plugin


def test_plugin_loader_static_package():
    loader = PluginLoader("tests.fakes", Plugin)
    discovered = loader.discover()
    names = [cls.__name__ for cls in discovered]
    assert "PluginOne" in names
