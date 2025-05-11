# SPDX-License-Identifier: MPL-2.0
"""
netimate.core.runner
--------------------
Declares :class:`RunnerInterface`, which abstracts the concurrent execution
engine responsible for applying a :class:`DeviceCommand` across one or many
:class:`netimate.models.device.Device` instances and returning structured
results.
"""

from typing import Any, List, Protocol

from netimate.interfaces.plugin.device_command import DeviceCommand
from netimate.models.device import Device


class RunnerInterface(Protocol):
    """
    Protocol for the asynchronous Runner.

    Implementations are expected to:
    1. Accept a list of resolved `Device` objects.
    2. Dispatch the provided `DeviceCommand` using the device's connection
       protocol.
    3. Return a list of per‑device result dictionaries that the calling
       view (CLI/Shell) can render.
    """

    async def run(self, devices: List[Device], command: DeviceCommand) -> List[dict[str, Any]]: ...
