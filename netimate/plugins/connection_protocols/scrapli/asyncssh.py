# SPDX-License-Identifier: MPL-2.0
"""
netimate.plugins.connection_protocols.asyncssh
----------------------------------------------
Scrapli‑based asynchronous SSH protocol plugin.

Picks a platform‑specific Scrapli driver (IOS‑XE, NX‑OS, Junos, etc.) based
on ``device.platform`` and exposes the common async `connect / send_command /
disconnect` contract required by :class:`ConnectionProtocol`.
"""
from os.path import expanduser
from typing import Dict

from scrapli.driver.core import (
    AsyncEOSDriver,
    AsyncIOSXEDriver,
    AsyncIOSXRDriver,
    AsyncJunosDriver,
    AsyncNXOSDriver,
)
from scrapli.driver.generic import AsyncGenericDriver

# Additional imports for error handling
from scrapli.exceptions import (
    ScrapliAuthenticationFailed,
    ScrapliConnectionError,
    ScrapliTimeout,
)

from netimate.errors import (
    AuthError,
    ConnectionProtocolError,
    ConnectionTimeoutError,
)
from netimate.interfaces.plugin.connection_protocol import ConnectionProtocol
from netimate.models.device import Device

PLATFORM_DRIVERS = {
    "ios": AsyncIOSXEDriver,
    "iosxe": AsyncIOSXEDriver,
    "nxos": AsyncNXOSDriver,
    "iosxr": AsyncIOSXRDriver,
    "eos": AsyncEOSDriver,
    "junos": AsyncJunosDriver,
}


class ScrapliAsyncsshConnectionProtocol(ConnectionProtocol):
    """
    Scrapli-based async SSH plugin that selects platform-aware drivers
    based on `platform` field in device config. Falls back to generic.
    """

    @staticmethod
    def plugin_name() -> str:
        return "scrapli-asyncssh"

    def __init__(self, device: Device, plugin_settings: Dict | None = None):
        """
        Parameters
        ----------
        device:
            :class:`netimate.models.device.Device` to connect to.
        plugin_settings:
            Optional mapping that may contain:
            * ``ssh_known_hosts_file`` – override path to known_hosts
            * ``transport_options``    – dict forwarded to Scrapli transport
        """
        super().__init__(device, plugin_settings)
        self.device = device
        self.client = None

    async def connect(self):
        if not self.device.platform:
            driver_cls = AsyncGenericDriver
        else:
            driver_cls = PLATFORM_DRIVERS.get(self.device.platform, AsyncGenericDriver)

        if self.plugin_settings:
            known_hosts_file = self.plugin_settings.get(
                "ssh_known_hosts_file", expanduser("~/.ssh/known_hosts")
            )
            transport_options = self.plugin_settings.get("transport_options", {})
        else:
            known_hosts_file = expanduser("~/.ssh/known_hosts")
            transport_options = {}

        self.client = driver_cls(
            host=self.device.host,
            auth_username=self.device.username,
            auth_password=self.device.password,
            auth_secondary=self.device.password,
            transport="asyncssh",
            transport_options=transport_options,
            ssh_known_hosts_file=known_hosts_file,
        )

        try:
            await self.client.open()
        except ScrapliAuthenticationFailed as err:
            raise AuthError() from err
        except ScrapliTimeout as err:
            raise ConnectionTimeoutError() from err
        except ScrapliConnectionError as err:
            raise ConnectionProtocolError("Connection failed") from err
        except Exception as err:  # pylint: disable=broad-except
            raise ConnectionProtocolError("Unexpected connection error") from err

    async def send_command(self, command: str) -> str:
        if not self.client:
            raise ConnectionProtocolError("No connection established; call .connect() first")

        try:
            response = await self.client.send_command(command)
            return response.result
        except ScrapliTimeout as err:
            raise ConnectionTimeoutError() from err
        except Exception as err:  # pylint: disable=broad-except
            raise ConnectionProtocolError("Failed to execute command") from err

    async def disconnect(self):
        if not self.client:
            return

        try:
            await self.client.close()
        except Exception as err:  # pylint: disable=broad-except
            raise ConnectionProtocolError("Failed to disconnect") from err
