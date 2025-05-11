# SPDX-License-Identifier: MPL-2.0
import logging
from typing import Any, Optional

from netimate.interfaces.plugin.device_command import DeviceCommand

logger = logging.getLogger(__name__)


class EchoTest(DeviceCommand):
    def template_file(self) -> Optional[str]:
        return None

    @staticmethod
    def plugin_name() -> str:
        return "echo-test"

    def command_string(self) -> str:
        return "echo test"

    def parse(self, raw_output: str):
        logger.debug(f"Parsing output in EchoTest: {raw_output.strip()}")
        return {"raw": raw_output.strip()}

    def format_result(self, result: Any) -> str:
        return result["raw"]
