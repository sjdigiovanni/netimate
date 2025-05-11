# SPDX-License-Identifier: MPL-2.0
from netimate.interfaces.plugin.plugin import Plugin


class Dummy(Plugin):
    @property
    def plugin_name(self):
        return "dummy"


def test_base_interface_name():
    d = Dummy()
    assert d.plugin_name == "dummy"
