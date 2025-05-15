# SPDX-License-Identifier: MPL-2.0
import asyncio

from netimate.errors import AuthError
from netimate.interfaces.plugin.connection_protocol import ConnectionProtocol
from netimate.models.device import Device


class FailingAsyncProtocol(ConnectionProtocol):
    def __init__(self, device: Device, plugin_settings: dict | None = None):
        self.device = device
        self.connected = False

    @staticmethod
    def plugin_name() -> str:  # type: ignore[override]
        # Unique name so we can assign devices to it
        return "failing-async"

    async def connect(self):  # type: ignore[override]
        raise AuthError("bad creds")

    async def send_command(self, command: str) -> str:
        await asyncio.sleep(0.6)
        return command

    async def disconnect(self):
        await asyncio.sleep(0.1)
        self.connected = False
