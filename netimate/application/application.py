# SPDX-License-Identifier: MPL-2.0
"""
netimate.application.application
--------------------------------
High–level orchestration layer that glues the CLI / shell views to the
core runner and plugin registry.  Responsible for:
• resolving device repositories and devices based on user input
• locating the correct plugin implementations (protocol, command, repo)
• delegating concurrent execution to the Runner
• utility helpers for diagnostics, snapshots, diffs and list‑style queries

This module is UI‑agnostic: both CLI commands and the interactive shell
call the same `Application` façade.
"""

import logging
from datetime import datetime
from difflib import unified_diff
from pathlib import Path
from typing import Dict, List, Optional

from netimate.infrastructure.logging import configure_logging
from netimate.interfaces.application.application import ApplicationInterface
from netimate.interfaces.core.registry import PluginRegistryInterface
from netimate.interfaces.core.runner import RunnerInterface
from netimate.interfaces.infrastructure.settings import SettingsInterface
from netimate.interfaces.infrastructure.template_provider import TemplateProviderInterface
from netimate.interfaces.plugin.connection_protocol import ConnectionProtocol
from netimate.interfaces.plugin.device_repository import DeviceRepository
from netimate.models.device import Device

logger = logging.getLogger(__name__)


class Application(ApplicationInterface):
    """
    Orchestrates execution of device commands across different UIs (CLI, shell, etc.).
    Resolves device repositories, filters devices, locates the appropriate command,
    and delegates execution to the runner.
    """

    def __init__(
        self,
        registry: PluginRegistryInterface,
        settings: SettingsInterface,
        runner: RunnerInterface,
        template_provider: TemplateProviderInterface,
    ) -> None:
        self._registry = registry
        self._settings = settings
        self._runner = runner
        self._template_provider = template_provider

    def get_template_provider(self) -> TemplateProviderInterface:
        """Return the singleton TemplateProvider injected at startup."""
        return self._template_provider

    def get_log_level(self) -> str:
        """Return the current log level from settings."""
        return self._settings.log_level

    def get_settings(self) -> SettingsInterface:
        """Return the application settings instance."""
        return self._settings

    def get_device_repository(self) -> DeviceRepository:
        """Return an instance of the configured device repository plugin."""
        repo_cls = self._registry.get_device_repository(self._settings.device_repo)
        return repo_cls(self._settings.plugin_configs.get(self._settings.device_repo))

    def get_protocol(self, name: str, device: Device) -> ConnectionProtocol:
        """Return a protocol instance for the given name and device."""
        protocol_cls = self._registry.get_protocol(name)
        return protocol_cls(device, self._settings.plugin_configs.get(name))

    def get_device_command(self, name: str):
        """Return a device command instance for the given command name."""
        return self._registry.get_device_command(name)(
            self._template_provider, self._settings.plugin_configs.get(name)
        )

    def expand_device_names(self, names: List[str]) -> List[str]:
        """
        Expand input names into real device names (devices or sites).
        """
        all_sites = self.list("sites")

        expanded = []
        for name in names:
            if name in all_sites:
                expanded.extend(self.list("devices", site=name))
            else:
                expanded.append(name)
        return expanded

    async def diagnostic(self, device_names: List[str]) -> Dict[str, Dict]:
        """
        Runs a health diagnostic across the specified devices, combining key checks into a report.
        Returns a formatted summary for each device.
        """
        device_names = self.expand_device_names(device_names)
        logger.info("Running diagnostics...")

        commands = [
            "show-version",
            "show-ip-interface-brief",
            "show-memory-stats",
            "show-processes-cpu",
            "show-logging",
        ]

        results_by_device: Dict[str, Dict] = {name: {} for name in device_names}
        for command in commands:
            try:
                command_results = await self.run_device_command(device_names, command)
                for device, output in command_results.items():
                    results_by_device[device][command] = output
            except Exception as e:
                for device in device_names:
                    results_by_device[device][command] = f"[error] {str(e)}"

        return results_by_device

    def list(self, key: str, site: Optional[str] = None) -> list[str]:
        """Return a list of items for the given key and optional site filter."""
        if not key:
            return [
                "Usage: list [devices|device-commands|device-repositories|snapshots|sites]",
                "",
                "Examples:",
                "  list devices",
                "  list snapshots",
            ]

        repo = self.get_device_repository()
        devices = repo.list_devices()
        match key:
            case "device-repositories":
                return [name for name in self._registry.all_device_repositories()]
            case "device-commands":
                return [name for name in self._registry.all_device_commands()]
            case "devices":
                if site:
                    devices = [d for d in devices if d.site == site]
                return [d.name for d in devices]
            case "sites":
                sites = sorted({d.site for d in devices if d.site})
                if not sites:
                    return ["[info] No sites found."]
                return sites
            case "snapshots":
                snapshot_dir = Path("snapshots")
                if not snapshot_dir.exists():
                    return ["[info] No snapshots directory found."]
                files = sorted(snapshot_dir.glob("*.txt"))
                if not files:
                    return ["[info] No snapshots found."]
                return [f"[{i}] {file.name}" for i, file in enumerate(files, 1)]
            case _:
                return [
                    f"[error] Unknown list key: {key}",
                    "Usage: list [devices|device-commands|device-repositories|snapshots]",
                ]

    async def run_device_command(
        self, device_names: List[str], command_name: str
    ) -> Dict[str, str]:
        """
        Executes a named device command across one or more target devices.

        Args:
            device_names: Names of devices to target.
            command_name: Registered name of the command to execute.

        Returns:
            List of parsed results or exceptions, one per device.
        """
        device_names = self.expand_device_names(device_names)
        logger.info("netimate execution started")

        # 1. Repository
        repository_cls = self._registry.get_device_repository(self._settings.device_repo)
        repository = repository_cls(self._settings.plugin_configs.get(self._settings.device_repo))
        devices = repository.list_devices()

        # 2. Resolve device(s)
        selected_devices = [d for d in devices if d.name in device_names]
        if len(selected_devices) != len(device_names):
            raise ValueError("One or more device names not found.")

        # 3. Command
        command_cls = self._registry.get_device_command(command_name)
        command = command_cls(self._template_provider)

        # 4. Run command on devices
        results = await self._runner.run(selected_devices, command)
        result_dict = {}

        for result in results:
            result_dict[result["device"]] = result["result"]

        return result_dict

    async def snapshot(self, device_names: List[str]) -> Dict[str, str]:
        """
        Takes a snapshot of the running config for each specified device
        and saves it to a timestamped file in the 'snapshots' directory.
        """
        device_names = self.expand_device_names(device_names)
        results = await self.run_device_command(device_names, "show-running-config")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_dir = Path("snapshots")
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        for device, output in results.items():
            file_path = snapshot_dir / f"{device}_running_config_{timestamp}.txt"
            if isinstance(output, dict) and "config_lines" in output:
                file_path.write_text("\n".join(output["config_lines"]))
            else:
                file_path.write_text(str(output))

        return results

    def set_log_level(self, level: str) -> None:
        """
        Set the application's log level.

        Args:
            level: The log level to set (e.g., 'info', 'debug', 'off').
        """
        configure_logging(level)
        self._settings.log_level = level

    def diff_snapshots(self, device: str, snap1: int | str, snap2: int | str) -> str:
        # Step 1: Resolve integers to filenames if necessary
        snapshots = self.list_snapshots_for_device(device)
        if isinstance(snap1, int):
            snap1 = snapshots[snap1 - 1]
        if isinstance(snap2, int):
            snap2 = snapshots[snap2 - 1]

        # Step 2: Load file contents
        text1 = (Path("snapshots") / snap1).read_text()
        text2 = (Path("snapshots") / snap2).read_text()

        # Step 3: Diff the files
        diff = unified_diff(
            text1.splitlines(),
            text2.splitlines(),
            fromfile=snap1,
            tofile=snap2,
            lineterm="",
        )

        return "\n".join(diff) or "No differences found."

    @staticmethod
    def list_snapshots_for_device(device: str) -> List[str]:
        snapshot_dir = Path("snapshots")
        if not snapshot_dir.exists():
            raise FileNotFoundError("No snapshots directory found.")

        device_snapshots = sorted(
            [f.name for f in snapshot_dir.glob(f"{device}_running_config_*.txt")]
        )
        if not device_snapshots:
            raise FileNotFoundError(f"No snapshots found for device {device}.")
        return device_snapshots
