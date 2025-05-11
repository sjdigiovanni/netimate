# SPDX-License-Identifier: MPL-2.0
from typing import Any

from netimate.interfaces.plugin.device_command import DeviceCommand


class ShowEnvironment(DeviceCommand):
    label = "Environment"
    table_headers = None  # summary is list[str]; keep plain text

    def template_file(self) -> str:
        return "ios/cisco_ios_show_environment_power_all.textfsm"

    @staticmethod
    def plugin_name() -> str:
        return "show-environment"

    def command_string(self) -> str:
        return "show environment"

    def summarise_result(self, result: Any) -> str:
        if "error" in result:
            return "Error parsing environment"
        if "summary" in result and result["summary"]:
            return f"{len(result['summary'])} checks OK"
        return "[no environment info]"
