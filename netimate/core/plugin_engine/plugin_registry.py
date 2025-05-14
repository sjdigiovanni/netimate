# SPDX-License-Identifier: MPL-2.0
from enum import Enum
from typing import Callable, Dict, Type

from netimate.errors import RegistryError
from netimate.interfaces.core.registry import PluginRegistryInterface
from netimate.interfaces.plugin.connection_protocol import ConnectionProtocol
from netimate.interfaces.plugin.device_command import DeviceCommand
from netimate.interfaces.plugin.device_repository import DeviceRepository
from netimate.interfaces.plugin.plugin import Plugin

"""
PluginRegistry is a central registry for plugins in the netimate application.
It maintains mappings of plugin names to their implementations for device commands,
connection protocols, and device repositories. This registry is used during
application boot to register and lookup plugins dynamically.
"""


class PluginKind(Enum):
    DEVICE_COMMAND = "device_command"
    PROTOCOL = "protocol"
    REPOSITORY = "repository"


class PluginRegistry(PluginRegistryInterface):
    """
    In‑memory implementation of the PluginRegistryInterface.
    Keeps three dictionaries keyed by plugin name and exposes helper
    methods for registration and lookup during application boot.
    """

    def __init__(self):
        self._device_commands: Dict[str, Type[DeviceCommand]] = {}
        self._protocols: Dict[str, Type[ConnectionProtocol]] = {}
        self._repositories: Dict[str, Type[DeviceRepository]] = {}

        self._handlers: Dict[PluginKind, Callable] = {
            PluginKind.DEVICE_COMMAND: self.register_device_command,
            PluginKind.PROTOCOL: self.register_protocol,
            PluginKind.REPOSITORY: self.register_device_repository,
        }

    def register(self, kind: PluginKind, name: str, plugin: Type[Plugin]):
        """Register a plugin of the specified kind under the given name."""
        if kind not in self._handlers:
            raise ValueError(f"Unknown plugin kind: {kind}")
        self._handlers[kind](name, plugin)

    def register_device_command(self, name: str, command_cls: Type[DeviceCommand]):
        """Register a DeviceCommand implementation under *name*."""
        self._device_commands[name] = command_cls

    def register_protocol(self, name: str, protocol_cls: Type[ConnectionProtocol]):
        """Register a ConnectionProtocol implementation under *name*."""
        self._protocols[name] = protocol_cls

    def register_device_repository(self, name: str, repo_cls: Type[DeviceRepository]):
        """Register a DeviceRepository implementation under *name*."""
        self._repositories[name] = repo_cls

    def get_device_command(self, name: str) -> Type[DeviceCommand]:
        """Return the DeviceCommand class registered under *name*."""
        try:
            return self._device_commands[name]
        except KeyError as e:
            raise RegistryError(f"No device command plugin named '{name}' is registered.") from e

    def get_protocol(self, name: str) -> type:
        try:
            return self._protocols[name]
        except KeyError as e:
            raise RegistryError(
                f"No connection protocol plugin named '{name}' is registered."
            ) from e

    def get_device_repository(self, name: str) -> Type[DeviceRepository]:
        """Return the DeviceRepository class registered under *name*."""
        try:
            return self._repositories[name]
        except KeyError as e:
            raise RegistryError(f"No repository plugin named '{name}' is registered.") from e

    def all_device_commands(self):
        """Return all registered device command names."""
        return self._device_commands.keys()

    def all_device_repositories(self):
        """Return all registered device repository names."""
        return self._repositories.keys()

    def all_protocols(self):
        """Return all registered protocol names."""
        return self._protocols.keys()
