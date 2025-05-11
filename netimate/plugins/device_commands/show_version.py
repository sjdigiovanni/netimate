# SPDX-License-Identifier: MPL-2.0
import logging
from typing import Dict, List

from netimate.interfaces.plugin.device_command import DeviceCommand

logger = logging.getLogger(__name__)


class ShowVersion(DeviceCommand):
    # Display metadata for Rich formatting
    label = "Platform Info"
    table_headers = [
        "HOSTNAME",
        "SOFTWARE_IMAGE",
        "VERSION",
        "UPTIME",
        "RUNNING_IMAGE",
        "ROMMON",
        "RELEASE",
    ]

    def summarise_result(self, result: List[Dict]) -> str:
        data = result[0]
        platform = data.get("SOFTWARE_IMAGE", "N/A")
        version = data.get("VERSION", "N/A")
        return f"{platform} - {version}"

    def template_file(self) -> str:
        return "ios/cisco_ios_show_version.textfsm"

    @staticmethod
    def plugin_name() -> str:
        return "show-version"

    def command_string(self) -> str:  # no args today
        return "show version"
