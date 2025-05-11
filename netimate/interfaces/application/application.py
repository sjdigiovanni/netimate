# SPDX-License-Identifier: MPL-2.0
from abc import abstractmethod
from typing import Dict, List, Protocol

from netimate.interfaces.infrastructure.settings import SettingsInterface
from netimate.interfaces.plugin.connection_protocol import ConnectionProtocol
from netimate.interfaces.plugin.device_repository import DeviceRepository
from netimate.models.device import Device


class ApplicationInterface(Protocol):  # pragma: no cover
    """
    Represents the main orchestration point for netimate application actions.

    Application implementations are responsible for coordinating execution
    across plugins and repositories based on user input and application state.
    """

    @abstractmethod
    def get_log_level(self) -> str: ...

    @abstractmethod
    def get_settings(self) -> SettingsInterface:
        """Return the application settings object."""
        ...

    @abstractmethod
    def get_device_repository(self) -> DeviceRepository:
        """Return the currently active device repository."""
        ...

    @abstractmethod
    def get_protocol(self, name: str, device: Device) -> ConnectionProtocol:
        """Return the protocol implementation by name."""
        ...

    @abstractmethod
    def list(self, key: str, site: str | None = None) -> List[str]:
        """
        Return a formatted string representation for the requested list.

        Valid keys: device-commands, device-repositories, etc.
        """
        ...

    @abstractmethod
    async def run_device_command(
        self, device_names: List[str], command_name: str
    ) -> Dict[str, str]:
        """
        Execute a device-level command against one or more devices.

        Args:
            device_names: List of device names to target.
            command_name: Name of the device command to run.

        Returns:
            List of parsed command results for each device.
        """
        ...

    @abstractmethod
    async def snapshot(self, device_names: List[str]) -> Dict[str, str]:
        """
        Capture and store the running configuration of the specified devices.

        Args:
            device_names: List of device identifiers.

        Returns:
            Dictionary mapping each device name to the file path of its saved config.
        """
        ...

    @abstractmethod
    async def diagnostic(self, device_names: List[str]) -> Dict[str, Dict]:
        """
        Run a full diagnostic suite against the specified devices.

        Args:
            device_names: List of device identifiers.

        Returns:
            Dictionary mapping each device name to its formatted diagnostic report.
        """
        ...

    @abstractmethod
    def set_log_level(self, level: str) -> None: ...

    def get_device_command(self, command_name):
        pass

    @abstractmethod
    def diff_snapshots(self, device: str, snap1: int | str, snap2: int | str) -> str:
        """
        Diff two snapshots of a device.

        Args:
            device: The device name.
            snap1: First snapshot ID or filename.
            snap2: Second snapshot ID or filename.

        Returns:
            A string representing the textual diff output.
        """
        ...

    @staticmethod
    @abstractmethod
    def list_snapshots_for_device(device: str) -> List[str]:
        """
        Given a device name, return a list of snapshots

        :param device:
        :return: List of str file paths to snapshots for the provided device
        """
        ...
