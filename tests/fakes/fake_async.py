# SPDX-License-Identifier: MPL-2.0
import asyncio

from netimate.interfaces.plugin.connection_protocol import ConnectionProtocol
from netimate.models.device import Device


class FakeAsyncProtocol(ConnectionProtocol):
    def __init__(self, device: Device, plugin_settings: dict | None = None):
        self.device = device
        self.connected = False

    @staticmethod
    def plugin_name() -> str:
        return "fake-async"

    async def connect(self):
        await asyncio.sleep(0.1)
        self.connected = True

    async def send_command(self, command: str) -> str:
        await asyncio.sleep(0.6)
        return command

    async def disconnect(self):
        await asyncio.sleep(0.1)
        self.connected = False
