# SPDX-License-Identifier: MPL-2.0
from typing import Dict, List

from netimate.interfaces.plugin.device_command import DeviceCommand


class ShowLogging(DeviceCommand):
    label = "System Logging"
    table_headers = ["MONTH", "DAY", "TIME", "FACILITY", "SEVERITY", "MNEMONIC", "MESSAGE"]

    def template_file(self) -> str:
        return "ios/cisco_ios_show_logging.textfsm"

    @staticmethod
    def plugin_name() -> str:
        return "show-logging"

    def command_string(self) -> str:
        return "show logging"

    def summarise_result(self, result: List[Dict]) -> str:
        if not result:
            return "[no log entries]"

        severity_labels = {
            "0": "Emergency",
            "1": "Alert",
            "2": "Critical",
            "3": "Error",
            "4": "Warning",
            "5": "Notice",
            "6": "Info",
            "7": "Debug",
        }

        severity_counts = {str(i): 0 for i in range(8)}
        for entry in result:
            sev = entry.get("SEVERITY")
            if sev in severity_counts:
                severity_counts[sev] += 1

        parts = []
        for sev, count in severity_counts.items():
            if count:
                label = severity_labels.get(sev, f"Severity {sev}")
                parts.append(f"{count}x {label}")

        return ", ".join(parts)
