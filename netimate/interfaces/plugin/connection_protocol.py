# SPDX-License-Identifier: MPL-2.0
"""
netimate.interfaces.plugin.connection_protocol
----------------------------------------------
Abstract base plugin class for any interactive connection mechanism
(SSH, Telnet, NETCONF, RESTCONF, Fake‑Async for tests, etc.).  Concrete
implementations are loaded at runtime by the PluginRegistry and used by
the Runner to execute device commands.
"""
from abc import abstractmethod
from typing import Dict

from netimate.interfaces.plugin.plugin import Plugin
from netimate.models.device import Device


class ConnectionProtocol(Plugin):  # pragma: no cover
    """
    Base class for all connection‑oriented plugins.

    Lifecycle:
    1. ``connect``     – open transport / login
    2. ``send_command`` – execute a single command string
    3. ``disconnect``  – cleanly close the session
    """

    @abstractmethod
    def __init__(self, device: Device, plugin_settings: Dict | None = None):
        """
        Parameters
        ----------
        device:
            Concrete :class:`netimate.models.device.Device` the protocol will
            talk to (holds IP, port, credentials).
        plugin_settings:
            Optional plugin‑specific configuration block from
            ``settings.plugin_configs``; may be ``None``.
        """
        super().__init__(plugin_settings)
        self.device = device

    @abstractmethod
    async def connect(self) -> None:
        """Open the underlying transport channel."""

    @abstractmethod
    async def send_command(self, command: str) -> str:
        """Run *command* and return raw screen string."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the transport and free resources."""
