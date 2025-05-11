# SPDX-License-Identifier: MPL-2.0
from typing import Any

from netimate.interfaces.plugin.device_command import DeviceCommand


class ShowRunningConfig(DeviceCommand):
    label = "Running Config"
    table_headers = None  # keep plain text

    def template_file(self) -> str:
        return ""

    @staticmethod
    def plugin_name() -> str:
        return "show-running-config"

    def command_string(self) -> str:
        return "show running-config"

    def parse(self, raw_output: str) -> dict[str, Any]:
        """
        Basic parser that captures raw config into lines. Could be extended for structured parsing.
        """
        lines = raw_output.strip().splitlines()
        return {"config_lines": lines}

    def format_result(self, result: Any) -> str:
        """
        Return the raw config as-is, or optionally formatted as JSON.
        """
        return "\n".join(result.get("config_lines", []))

    def summarise_result(self, result: Any) -> str:
        if not result or not isinstance(result, dict):
            return "[no output]"
        return f"{len(result.get('config_lines', []))} lines of config"
