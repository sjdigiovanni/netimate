# SPDX-License-Identifier: MPL-2.0
from enum import Enum
from typing import Callable, Dict, Type

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
        self.device_commands: Dict[str, Type[DeviceCommand]] = {}
        self.protocols: Dict[str, Type[ConnectionProtocol]] = {}
        self.repositories: Dict[str, Type[DeviceRepository]] = {}

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
        self.device_commands[name] = command_cls

    def register_protocol(self, name: str, protocol_cls: Type[ConnectionProtocol]):
        """Register a ConnectionProtocol implementation under *name*."""
        self.protocols[name] = protocol_cls

    def register_device_repository(self, name: str, repo_cls: Type[DeviceRepository]):
        """Register a DeviceRepository implementation under *name*."""
        self.repositories[name] = repo_cls

    def get_device_command(self, name: str) -> Type[DeviceCommand]:
        """Return the DeviceCommand class registered under *name*."""
        return self.device_commands[name]

    def get_protocol(self, name: str) -> Type[ConnectionProtocol]:
        """Return the ConnectionProtocol class registered under *name*."""
        return self.protocols[name]

    def get_device_repository(self, name: str) -> Type[DeviceRepository]:
        """Return the DeviceRepository class registered under *name*."""
        return self.repositories[name]

    def all_device_commands(self):
        """Return all registered device command names."""
        return self.device_commands.keys()

    def all_device_repositories(self):
        """Return all registered device repository names."""
        return self.repositories.keys()

    def all_protocols(self):
        """Return all registered protocol names."""
        return self.protocols.keys()
