# SPDX-License-Identifier: MPL-2.0
from typing import Dict, List, Tuple

from netimate.interfaces.core.registry import PluginRegistryInterface
from netimate.interfaces.core.runner import RunnerInterface
from netimate.interfaces.infrastructure.settings import SettingsInterface
from netimate.interfaces.infrastructure.template_provider import TemplateProviderInterface
from netimate.interfaces.plugin.connection_protocol import ConnectionProtocol
from netimate.interfaces.plugin.device_repository import DeviceRepository
from netimate.models.device import Device


class CommandExecutorService:
    def __init__(
        self,
        registry: PluginRegistryInterface,
        settings: SettingsInterface,
        template_provider: TemplateProviderInterface,
        runner: RunnerInterface,
    ):
        self._registry = registry
        self._settings = settings
        self._template_provider = template_provider
        self._runner = runner

    async def run(self, device_names: List[str], command_name: str) -> Dict[str, str]:
        """
        Run a command on the given list of device names.
        Note: device_names should be pre-expanded and must correspond exactly to device names.
        """
        repository_cls = self._registry.get_device_repository(self._settings.device_repo)
        repository: DeviceRepository = repository_cls(
            self._settings.plugin_configs.get(self._settings.device_repo)
        )
        devices = repository.list_devices()

        selected_devices = [d for d in devices if d.name in device_names]
        if len(selected_devices) != len(device_names):
            raise ValueError("One or more device names not found.")

        command_cls = self._registry.get_device_command(command_name)
        command = command_cls(self._template_provider)

        device_protocol_pairs: List[Tuple[Device, ConnectionProtocol]] = []
        for device in selected_devices:
            protocol_name = device.protocol
            protocol_cls = self._registry.get_protocol(protocol_name)
            protocol_config: str | Dict = self._settings.plugin_configs.get(protocol_name, {})
            protocol = protocol_cls(protocol_config)
            device_protocol_pairs.append((device, protocol))

        results = await self._runner.run(device_protocol_pairs, command)
        return {r["device"]: r["result"] for r in results}
