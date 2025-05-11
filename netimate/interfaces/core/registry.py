# SPDX-License-Identifier: MPL-2.0
"""
netimate.core.plugin_engine.registry
------------------------------------
Defines :class:`PluginRegistryInterface`, a Protocol describing the public
surface of any registry implementation that stores references to plugin
classes (DeviceCommand, ConnectionProtocol, DeviceRepository).  The concrete
in‑memory implementation lives in `plugin_registry.py`.
"""

from typing import Any, Iterable, Protocol, Type

from netimate.interfaces.plugin.connection_protocol import ConnectionProtocol
from netimate.interfaces.plugin.device_command import DeviceCommand
from netimate.interfaces.plugin.device_repository import DeviceRepository
from netimate.interfaces.plugin.plugin import Plugin


# Protocol describing the public interface of PluginRegistry
class PluginRegistryInterface(Protocol):
    """
    Structural typing interface for a plugin registry.

    A registry maps a **string name** (e.g. ``"ssh"``, ``"show-version"``)
    to a concrete plugin class.  It exposes helper methods for registration
    and lookup, plus convenience `all_*` iterators so UIs can enumerate
    available commands, protocols, and repositories.
    """

    def register(self, kind: "Any", name: str, plugin: Type[Plugin]) -> None: ...
    def register_device_command(self, name: str, command_cls: Type[DeviceCommand]) -> None: ...
    def register_protocol(self, name: str, protocol_cls: Type[ConnectionProtocol]) -> None: ...
    def register_device_repository(self, name: str, repo_cls: Type[DeviceRepository]) -> None: ...
    def get_device_command(self, name: str) -> "Type": ...
    def get_protocol(self, name: str) -> "Type": ...
    def get_device_repository(self, name: str) -> "Type": ...
    def all_device_commands(self) -> "Iterable[str]": ...
    def all_device_repositories(self) -> "Iterable[str]": ...
    def all_protocols(self) -> "Iterable[str]": ...
