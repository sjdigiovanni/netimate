# SPDX-License-Identifier: MPL-2.0
import asyncio
import logging
from typing import Any, Dict, List, Tuple

from netimate.errors import NetimateError, RunnerError
from netimate.interfaces.core.runner import RunnerInterface
from netimate.interfaces.plugin.connection_protocol import ConnectionProtocol
from netimate.interfaces.plugin.device_command import DeviceCommand
from netimate.models.device import Device

logger = logging.getLogger(__name__)


class Runner(RunnerInterface):
    """
    Orchestrates parallel command execution across multiple devices.
    Selects appropriate runner per device using RunnerSelector.
    """

    def __init__(self, plugin_configs: Dict[str, Any]):
        self.plugin_configs = plugin_configs

    async def run(
        self, device_protocols: List[Tuple[Device, ConnectionProtocol]], command: DeviceCommand
    ) -> (List)[dict[str, Any]]:
        """
        Executes the command on all devices concurrently using their associated protocol instances.

        Returns:
            A list of results (or errors) per device.
        """
        tasks = [
            self._run_on_device(device, protocol, command) for device, protocol in device_protocols
        ]
        return await asyncio.gather(*tasks)

    async def _run_on_device(
        self, device: Device, protocol: ConnectionProtocol, command: DeviceCommand
    ) -> Dict[str, Any]:
        """
        Execute *command* on *device* using the provided *protocol* instance and return a structured per‑device result.

        The method guarantees that no third‑party exceptions leak; any unexpected
        error is wrapped as ``RunnerError``.  The shape of the returned dict is::

            {
                "device": "<hostname>",
                "success": bool,
                "result": <parsed output>|None,
                "error": "<error message>"|None,
                "error_type": "<ExceptionClassName>"|None,
            }
        """
        logger.info(
            "[Runner] Running '%s' on '%s'",
            command.command_string(),
            device.name,
        )

        try:
            await protocol.connect()
            logger.debug("Connected to %s", device.host)

            raw_output = await protocol.send_command(command.command_string())
            logger.debug("Raw output: %s", raw_output)

            await protocol.disconnect()
            logger.debug("Disconnected from %s", device.host)

            parsed = command.parse(raw_output)
            logger.info("Parsed result for %s: %s", device.name, parsed)

            return {
                "device": device.name,
                "success": True,
                "result": parsed,
                "error": None,
                "error_type": None,
            }

        except NetimateError as err:
            # Expected, domain‑specific failure (connection, auth, registry, etc.)
            logger.warning("Netimate error on %s: %s", device.name, err)
            return {
                "device": device.name,
                "success": False,
                "result": str(err),
                "error": str(err),
                "error_type": err.__class__.__name__,
            }

        except Exception as err:  # pylint: disable=broad-except
            # Unexpected bug – wrap in RunnerError so upper layers stay clean
            logger.exception("Unexpected error on %s", device.name, exc_info=err)
            wrapped = RunnerError("Unexpected runner failure")
            wrapped.__cause__ = err
            return {
                "device": device.name,
                "success": False,
                "result": str(err),
                "error": str(wrapped),
                "error_type": "RunnerError",
            }
