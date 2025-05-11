# SPDX-License-Identifier: MPL-2.0
from netimate.interfaces.plugin.plugin import Plugin


class PluginOne(Plugin):
    @staticmethod
    def plugin_name() -> str:
        return "plugin-one"
