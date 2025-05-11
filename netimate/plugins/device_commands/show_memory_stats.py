# SPDX-License-Identifier: MPL-2.0
from typing import Dict, List

from netimate.interfaces.plugin.device_command import DeviceCommand


class ShowMemoryStats(DeviceCommand):
    label = "Memory Stats"
    # Rich table columns to be auto‑rendered by DeviceCommand
    table_headers = ["TOTAL_BYTES", "USED_BYTES", "FREE_BYTES"]

    def template_file(self) -> str:
        return "ios/cisco_ios_show_memory_stats.textfsm"

    @staticmethod
    def plugin_name() -> str:
        return "show-memory-stats"

    def command_string(self) -> str:
        return "show memory statistics"

    # show_memory_stats.py
    def summarise_result(self, result: List[Dict]) -> str:
        if not result:
            return "[no output]"

        try:
            stats = result[0]
            total = int(stats["TOTAL_BYTES"])
            used = int(stats["USED_BYTES"])
            percent = (used / total) * 100 if total else 0
            status = "OK" if percent < 85 else "⚠️ HIGH"
            return (
                f"{used / 1_000_000:.1f}MB "
                f"/ {total / 1_000_000:.1f}MB ({percent:.1f}%) — {status}"
            )
        except (KeyError, ValueError):
            return "[parse error]"
