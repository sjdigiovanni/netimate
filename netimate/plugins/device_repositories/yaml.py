# SPDX-License-Identifier: MPL-2.0
import logging
from typing import Dict, List

import yaml

from netimate.infrastructure.utils.file_management import find_file_upward
from netimate.interfaces.plugin.device_repository import DeviceRepository
from netimate.models.device import Device

logger = logging.getLogger(__name__)


class YamlDeviceRepository(DeviceRepository):
    def __init__(self, plugin_settings: Dict):
        super().__init__()
        self._yaml_config = plugin_settings
        if not self._yaml_config:
            raise ValueError("Settings file missing yaml config!")
        if not self._yaml_config.get("device_file"):
            raise ValueError("Settings file missing yaml.device_file!")
        else:
            self._device_file: str = self._yaml_config["device_file"]

    @staticmethod
    def plugin_name() -> str:
        return "yaml"

    def list_devices(self) -> List[Device]:
        logger.info(f"Loading all devices from YAML: {self._device_file}")
        path = find_file_upward(self._device_file)
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        devices = [Device(**item) for item in data.get("devices", [])]
        logger.debug(f"Loaded devices: {devices}")
        return devices
