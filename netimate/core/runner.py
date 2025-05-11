# SPDX-License-Identifier: MPL-2.0
import asyncio
import logging
from typing import Any, Dict, List

from netimate.core.plugin_engine.plugin_registry import PluginRegistry
from netimate.interfaces.core.runner import RunnerInterface
from netimate.interfaces.plugin.device_command import DeviceCommand
from netimate.models.device import Device

logger = logging.getLogger(__name__)


class Runner(RunnerInterface):
    """
    Orchestrates parallel command execution across multiple devices.
    Selects appropriate runner per device using RunnerSelector.
    """

    def __init__(self, registry: PluginRegistry, plugin_configs: Dict[str, Any]):
        self.registry = registry
        self.plugin_configs = plugin_configs

    async def run(self, devices: List[Device], command: DeviceCommand) -> List[dict[str, Any]]:
        """
        Executes the command on all devices concurrently.

        Returns:
            A list of results (or errors) per device.
        """
        tasks = [self._run_on_device(device, command) for device in devices]
        return await asyncio.gather(*tasks)

    async def _run_on_device(self, device: Device, command: DeviceCommand) -> Dict[str, Any]:
        """
        Executes a command on a single device using the appropriate runner.
        """
        logger.info(
            f"[Runner] Running command '{command.command_string()}'" f" on device '{device.name}'"
        )

        try:
            plugin_settings = self.plugin_configs.get(device.protocol, {})
            protocol = self.registry.get_protocol(device.protocol)(device, plugin_settings)
            await protocol.connect()
            logger.debug(f"Connected to {device.host}")

            output = await protocol.send_command(command.command_string())
            logger.debug(f"Received raw output: {output}")

            await protocol.disconnect()
            logger.debug(f"Disconnected from {device.host}")

            parsed = command.parse(output)
            logger.info(f"Parsed result: {parsed}")
            return {"device": device.name, "success": True, "result": parsed}
        except Exception as e:
            logger.exception(f"Error running command on {device.name}: {e}")
            return {"device": device.name, "success": False, "error": str(e)}
