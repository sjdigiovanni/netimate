# SPDX-License-Identifier: MPL-2.0
"""
netimate.infrastructure.settings
--------------------------------
Concrete implementation of :class:`SettingsInterface` that holds runtime
configuration loaded from YAML (see ``config_loader.py``).  The object is
immutable except for the ``log_level`` property, which can be toggled at
runtime by the shell or CLI to increase verbosity.
"""

from pathlib import Path
from typing import Dict

from netimate.interfaces.infrastructure.settings import SettingsInterface


class SettingsImpl(SettingsInterface):
    def __init__(
        self,
        device_repo: str,
        log_level: str,
        template_paths: list[str],
        plugin_configs: Dict | None = None,
    ):
        """
        Parameters
        ----------
        device_repo:
            Dotted import path of the DeviceRepository plugin to use by default.
        log_level:
            One of ``"off"``, ``"info"``, ``"debug"``; forwarded to
            `infrastructure.logging.configure_logging`.
        template_paths:
            Additional directories (absolute or relative) that contain
            ``*.textfsm`` or ``*.ttp`` templates.  Merged with built‑in defaults.
        plugin_configs:
            Optional mapping passed verbatim to plugin constructors so each
            plugin can read its own configuration block.
        """
        self._device_repo = device_repo
        self._log_level = log_level
        self._template_paths = template_paths
        if plugin_configs is None:
            self._plugin_configs = dict()
        else:
            self._plugin_configs = plugin_configs

    @property
    def device_repo(self) -> str:
        return self._device_repo

    @property
    def log_level(self) -> str:
        return self._log_level

    @log_level.setter
    def log_level(self, value: str) -> None:
        self._log_level = value

    @property
    def plugin_configs(self) -> Dict:
        return self._plugin_configs or dict()

    @property
    def template_paths(self) -> list[str]:
        """Return user‑specified template directories merged with built‑ins."""
        defaults = [
            # path relative to this file -> ../../plugins/device_commands/templates
            str(Path(__file__).parent.parent / "plugins" / "device_commands" / "templates"),
            str(Path(__file__).parent.parent / "templates"),
        ]
        return [*defaults, *self._template_paths]
