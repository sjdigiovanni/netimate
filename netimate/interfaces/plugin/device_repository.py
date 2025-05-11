# SPDX-License-Identifier: MPL-2.0
"""
netimate.interfaces.plugin.device_repository
--------------------------------------------
Abstract plugin base for discovering and returning :class:`Device` instances
from arbitrary backends (YAML file, REST API, SQL DB, etc.).  Implementations
are looked up via the PluginRegistry when the Application starts.
"""
from abc import abstractmethod
from typing import Dict, List

from netimate.interfaces.plugin.plugin import Plugin
from netimate.models.device import Device


class DeviceRepository(Plugin):  # pragma: no cover
    """
    Base class for device data‑source plugins.

    A repository's responsibility is to return a list of concrete
    :class:`netimate.models.device.Device` objects that the Runner can act
    upon.  Typical implementations include static YAML files or dynamic
    lookups from an IPAM/CMDB.
    """

    @abstractmethod
    def __init__(self, plugin_settings: Dict | None = None):
        """
        Parameters
        ----------
        plugin_settings:
            Optional mapping passed from ``settings.plugin_configs`` for this
            repository instance (e.g. API tokens, file paths).
        """
        super().__init__(plugin_settings)

    @abstractmethod
    def list_devices(self) -> List[Device]:
        """List all available devices."""
        pass
