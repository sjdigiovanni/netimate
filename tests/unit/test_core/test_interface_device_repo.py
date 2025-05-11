# SPDX-License-Identifier: MPL-2.0
from netimate.interfaces.plugin.device_repository import DeviceRepository


class DummyDeviceRepo(DeviceRepository):

    def __init__(self, device_file="test"):
        self.device_file = device_file

    @staticmethod
    def plugin_name() -> str:
        return "dummy"

    def list_devices(self):
        return ["R1", "R2"]


def test_device_repository_contract():
    repo = DummyDeviceRepo()
    assert ["R1", "R2"] == repo.list_devices()
