# SPDX-License-Identifier: MPL-2.0
"""
netimate.plugins.connection_protocols.telnet
--------------------------------------------
Netmiko Telnet protocol plugin wrapped in asyncio.  Provided mainly for
legacy devices that only expose a Telnet management channel.
"""

import asyncio
import logging

from netmiko import (
    ConnectHandler,
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)

from netimate.errors import (
    AuthError,
    ConnectionProtocolError,
    ConnectionTimeoutError,
)
from netimate.interfaces.plugin.connection_protocol import ConnectionProtocol
from netimate.models.device import Device

logger = logging.getLogger(__name__)


class NetmikoTelnetConnectionProtocol(ConnectionProtocol):
    """Async wrapper around Netmiko's Telnet ConnectHandler."""

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
        return "netmiko-telnet"

    async def connect(self):
        """Open a Netmiko Telnet session asynchronously."""
        loop = asyncio.get_running_loop()
        logger.info(f"Connecting to {self.device.host} via Telnet")
        try:
            self.connection = await loop.run_in_executor(
                None,
                lambda: ConnectHandler(
                    device_type="cisco_ios_telnet",
                    host=self.device.host,
                    username=self.device.username,
                    password=self.device.password,
                ),
            )
        except NetmikoAuthenticationException as err:
            raise AuthError() from err
        except NetmikoTimeoutException as err:
            raise ConnectionTimeoutError() from err
        except Exception as err:  # pylint: disable=broad-except
            raise ConnectionProtocolError("Unexpected connection error") from err

    async def send_command(self, command: str) -> str:
        """Send *command* over the Telnet session."""
        loop = asyncio.get_running_loop()
        if self.connection is None:
            raise ConnectionProtocolError("Connection not established")

        try:
            logger.info(f"Sending command over Telnet: {command}")
            return await loop.run_in_executor(None, self.connection.send_command, command)
        except Exception as err:  # pylint: disable=broad-except
            raise ConnectionProtocolError("Failed to execute command") from err

    async def disconnect(self):
        """Close the Telnet session."""
        if self.connection is None:
            return

        loop = asyncio.get_running_loop()
        try:
            logger.info(f"Disconnecting from {self.device.host}")
            await loop.run_in_executor(None, self.connection.disconnect)
        except Exception as err:  # pylint: disable=broad-except
            raise ConnectionProtocolError("Failed to disconnect") from err
