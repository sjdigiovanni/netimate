# SPDX-License-Identifier: MPL-2.0
"""
netimate.interfaces.plugin.plugin
--------------------------------
Abstract base class for every plugin type (DeviceCommand, ConnectionProtocol,
DeviceRepository).  Stores the `plugin_settings` dictionary parsed from
``settings.plugin_configs`` so each plugin can retrieve its own configuration
values without touching global state.
"""
from abc import ABC, abstractmethod
from typing import Dict


class Plugin(ABC):  # pragma: no cover
    """
    Root ABC for all plugin subclasses.

    Subclasses must implement the class‑method ``plugin_name`` which returns
    the canonical registry key under which the plugin will be registered
    (e.g. ``"ssh"``, ``"show-version"``, ``"filesystem-repo"``).
    """

    def __init__(self, plugin_settings: Dict | None = None):
        """
        Parameters
        ----------
        plugin_settings:
            Optional dictionary extracted from ``settings.plugin_configs``.
            Plugins are free to define and validate their own keys.
        """
        self.plugin_settings = plugin_settings

    @staticmethod
    @abstractmethod
    def plugin_name() -> str:
        """Return the registry key that identifies this plugin."""
        pass
