# SPDX-License-Identifier: MPL-2.0
from typing import Dict, List

from netimate.interfaces.plugin.device_command import DeviceCommand


class ShowProcessCpu(DeviceCommand):

    label = "CPU Stats"
    table_headers = ["CPU_USAGE_5_SEC", "PROCESS_NAME", "PROCESS_CPU_USAGE_5_SEC"]

    def template_file(self) -> str:
        return "ios/cisco_ios_show_processes_cpu.textfsm"

    @staticmethod
    def plugin_name() -> str:
        return "show-processes-cpu"

    def command_string(self) -> str:
        return "show processes cpu sorted | exclude 0.00%"

    def summarise_result(self, result: List[Dict]) -> str:
        if not result:
            return "[no output]"

        try:
            usage = int(result[0].get("CPU_USAGE_5_SEC", "0"))
            status = "OK" if usage < 85 else "⚠️ HIGH"
            return f"{usage}% (5s avg) — {status}"
        except (KeyError, ValueError):
            return "[parse error]"
