# SPDX-License-Identifier: MPL-2.0
import logging
from typing import Dict, List

from netimate.interfaces.plugin.device_command import DeviceCommand

logger = logging.getLogger(__name__)


class ShowIpInterfaceBrief(DeviceCommand):
    label = "Interfaces (IP Brief)"
    table_headers = ["INTERFACE", "IP_ADDRESS", "STATUS", "PROTO"]

    def template_file(self) -> str:
        return "ios/cisco_ios_show_ip_interface_brief.textfsm"

    @staticmethod
    def plugin_name() -> str:
        return "show-ip-interface-brief"

    def command_string(self) -> str:
        return "show ip interface brief"

    def summarise_result(self, result: List[Dict]) -> str:
        if not result:
            return "[no interface info]"
        up = sum(1 for i in result if i.get("STATUS") == "up")
        down = sum(1 for i in result if i.get("STATUS") != "up")
        return f"{up} up, {down} down"
