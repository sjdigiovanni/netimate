# SPDX-License-Identifier: MPL-2.0
from netimate.interfaces.plugin.device_command import DeviceCommand


class DummyCommand(DeviceCommand):
    def __init__(self, template_provider):
        super().__init__(template_provider)

    def template_file(self) -> str:
        return ""

    @property
    def plugin_name(self):
        return "dummy-command"

    def command_string(self, **kwargs):
        return "echo test"

    def parse(self, output):
        return {"raw": output}

    def format_result(self, result):
        return str(result)


def test_command_interface_contract():
    class MockTemplateProvider:
        def parse(self, template_file, output):
            return {"raw": output}

    mock_provider = MockTemplateProvider()
    cmd = DummyCommand(template_provider=mock_provider)
    assert cmd.plugin_name == "dummy-command"
    assert "echo" in cmd.command_string()
    parsed = cmd.parse("hello")
    assert parsed["raw"] == "hello"
    assert cmd.format_result(parsed) == str(parsed)
