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

        await self.client.open()

    async def send_command(self, command: str) -> str:
        if not self.client:
            raise ValueError("No connection established! Call .connect()")
        response = await self.client.send_command(command)
        return response.result

    async def disconnect(self):
        await self.client.close()
