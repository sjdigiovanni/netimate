# SPDX-License-Identifier: MPL-2.0
from netimate.infrastructure.settings import SettingsImpl


def test_settings_template_paths_default():
    s = SettingsImpl("test", "test", "test", ["test"])
    tpl_paths = s.template_paths
    assert any("device_commands/templates" in p for p in tpl_paths)
