# SPDX-License-Identifier: MPL-2.0
from netimate.interfaces.plugin.connection_protocol import ConnectionProtocol


class DummyProtocol(ConnectionProtocol):

    def __init__(self, device="test"):
        self.device = device

    @staticmethod
    def plugin_name() -> str:
        return "dummy"

    def connect(self):
        return "connected"

    def send_command(self, cmd):
        return f"sent: {cmd}"

    def disconnect(self):
        return "disconnected"


def test_protocol_contract():
    p = DummyProtocol()
    assert p.connect() == "connected"
    assert p.send_command("show version") == "sent: show version"
    assert p.disconnect() == "disconnected"
