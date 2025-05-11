# SPDX-License-Identifier: MPL-2.0
"""
netimate.plugins.connection_protocols.ssh
-----------------------------------------
Synchronous Netmiko‑based SSH protocol wrapped in asyncio using
`run_in_executor()`.  Provides an easy fallback for devices that are
supported by Netmiko but not yet by Scrapli.
"""

import asyncio
import logging

from netmiko import ConnectHandler

from netimate.interfaces.plugin.connection_protocol import ConnectionProtocol
from netimate.models.device import Device

logger = logging.getLogger(__name__)


class NetmikoSSHConnectionProtocol(ConnectionProtocol):
    """
    Netmiko‑powered SSH plugin.

    Uses `asyncio.get_running_loop().run_in_executor()` to off‑load the
    blocking Netmiko ConnectHandler into a thread pool so the rest of the
    application remains non‑blocking.
    """

    def __init__(self, device: Device):
        """
        Parameters
        ----------
        device:
            :class:`netimate.models.device.Device` connection parameters for
            the target host (host, username, password, etc.).
        """
        super().__init__(device)
        self.device = device
        self.connection = None

    @staticmethod
    def plugin_name() -> str:
        return "netmiko-ssh"

    async def connect(self):
        """Open a Netmiko SSH session asynchronously."""
        loop = asyncio.get_running_loop()
        logger.info(f"Connecting to {self.device.host} via SSH")
        self.connection = await loop.run_in_executor(
            None,
            lambda: ConnectHandler(
                device_type="cisco_ios",
                host=self.device.host,
                username=self.device.username,
                password=self.device.password,
            ),
        )

    async def send_command(self, command: str) -> str:
        """Send *command* over the established SSH connection."""
        loop = asyncio.get_running_loop()
        logger.info(f"Sending command over SSH: {command}")
        if self.connection is None:
            raise RuntimeError("Connection not established")

        return await loop.run_in_executor(None, self.connection.send_command, command)

    async def disconnect(self):
        """Cleanly close the Netmiko SSH session."""
        loop = asyncio.get_running_loop()
        logger.info(f"Disconnecting from {self.device.host}")
        await loop.run_in_executor(None, self.connection.disconnect)
