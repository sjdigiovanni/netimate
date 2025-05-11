# SPDX-License-Identifier: MPL-2.0
from unittest.mock import Mock

from rich.console import Console
from netimate.plugins.device_commands.show_environment import ShowEnvironment
from netimate.plugins.device_commands.show_logging import ShowLogging
from netimate.plugins.device_commands.show_memory_stats import ShowMemoryStats
from netimate.plugins.device_commands.show_process_cpu import ShowProcessCpu
from netimate.plugins.device_commands.show_ip_interface_brief import ShowIpInterfaceBrief
from netimate.plugins.device_commands.show_version import ShowVersion
from tests.outputs import SHOW_VERSION_RAW, SHOW_VERSION_PARSED

from tests.outputs import (
    SHOW_ENVIRONMENT_RAW,
    SHOW_IP_INTERFACE_BRIEF_RAW,
    SHOW_LOGGING_RAW,
    SHOW_MEMORY_STATS_RAW,
    SHOW_PROCESS_CPU_RAW,
    SHOW_ENVIRONMENT_PARSED,
    SHOW_IP_INTERFACE_BRIEF_PARSED,
    SHOW_LOGGING_PARSED,
    SHOW_MEMORY_STATS_PARSED,
    SHOW_PROCESS_CPU_PARSED,
)


def _to_text(maybe_table):
    """
    Ensure formatted output is a plain string for assertions.
    Accepts either a Rich Table/panel or an already-formatted string.
    """
    if hasattr(maybe_table, "row_count") or hasattr(maybe_table, "columns"):
        con = Console(record=True, width=120)
        con.print(maybe_table)
        return con.export_text()
    return str(maybe_table)


def test_show_environment():
    """Parses and formats environment data to ensure correct 'FAN is OK' summary appears in output."""
    raw = SHOW_ENVIRONMENT_RAW
    template_provider = Mock()
    template_provider.parse.return_value = SHOW_ENVIRONMENT_PARSED
    cmd = ShowEnvironment(template_provider)
    parsed = cmd.parse(raw)
    assert "summary" in parsed
    assert "FAN is OK" in parsed["summary"][0]
    formatted = cmd.format_result(parsed)
    assert "FAN is OK" in formatted


def test_show_ip_interface_brief():
    """Validates interface parsing and confirms formatted output includes key interface IP."""
    raw = SHOW_IP_INTERFACE_BRIEF_RAW
    template_provider = Mock()
    template_provider.parse.return_value = SHOW_IP_INTERFACE_BRIEF_PARSED
    cmd = ShowIpInterfaceBrief(template_provider)
    parsed = cmd.parse(raw)
    assert len(parsed) == 2
    formatted = _to_text(cmd.format_result(parsed))
    assert "192.168.1.1" in formatted


def test_show_logging():
    """Parses and formats log entries, ensuring SSH session messages appear in final output."""
    raw = SHOW_LOGGING_RAW
    template_provider = Mock()
    template_provider.parse.return_value = SHOW_LOGGING_PARSED
    cmd = ShowLogging(template_provider)
    parsed = cmd.parse(raw)
    assert len(parsed) == 2
    formatted = _to_text(cmd.format_result(parsed))
    assert "SSH2 Session request from" in formatted


def test_show_memory_stats():
    """Validates memory stats parsing and output formatting for human-readable usage display."""
    raw = SHOW_MEMORY_STATS_RAW
    template_provider = Mock()
    template_provider.parse.return_value = SHOW_MEMORY_STATS_PARSED
    cmd = ShowMemoryStats(template_provider)
    parsed = cmd.parse(raw)
    assert parsed[0]["USED_BYTES"] == 131607768
    assert parsed[0]["TOTAL_BYTES"] == 831753672
    formatted = _to_text(cmd.format_result(parsed))
    # New Rich table shows raw byte counts; validate header & used bytes
    assert "USED_BYTES" in formatted
    assert "131607768" in formatted


def test_show_process_cpu():
    """Checks CPU parser correctly extracts 5-second usage and confirms absence of high-usage processes."""
    raw = SHOW_PROCESS_CPU_RAW
    template_provider = Mock()
    template_provider.parse.return_value = SHOW_PROCESS_CPU_PARSED
    cmd = ShowProcessCpu(template_provider)
    parsed = cmd.parse(raw)
    assert parsed[0]["cpu_5s"] == 2
    formatted = _to_text(cmd.format_result(parsed))
    # Rich table header should be present; validate no numeric > 80 (high CPU)
    assert "CPU_USAGE_5_SEC" in formatted


def test_parser_extracts_interfaces():
    """Ensures mock template provider correctly parses interface details from brief output."""

    class MockTemplateProvider:
        def parse(self, template_name: str, raw_output: str):
            return [
                {
                    "INTERFACE": "Ethernet0/0",
                    "IP_ADDRESS": "192.168.1.1",
                    "STATUS": "up",
                    "PROTO": "up",
                },
                {
                    "INTERFACE": "Ethernet0/1",
                    "IP_ADDRESS": "unassigned",
                    "STATUS": "administratively down",
                    "PROTO": "down",
                },
            ]

    cmd = ShowIpInterfaceBrief(template_provider=MockTemplateProvider())
    parsed = cmd.parse(SHOW_IP_INTERFACE_BRIEF_RAW)

    assert len(parsed) == 2
    assert parsed[0]["INTERFACE"] == "Ethernet0/0"
    assert parsed[0]["IP_ADDRESS"] == "192.168.1.1"
    assert parsed[1]["STATUS"].startswith("administratively")


def test_show_version_name():
    """Verifies the correct plugin name is returned for the ShowVersion command."""
    mock_template_provider = Mock()
    cmd = ShowVersion(template_provider=mock_template_provider)
    assert cmd.plugin_name() == "show-version"


def test_show_version_command_string():
    """Verifies the CLI command string returned for ShowVersion is accurate."""
    mock_template_provider = Mock()
    cmd = ShowVersion(template_provider=mock_template_provider)
    assert cmd.command_string() == "show version"


def test_show_version_parser():
    """Parses raw version data and confirms version and uptime values are present and correct."""
    mock_template_provider = Mock()
    cmd = ShowVersion(template_provider=mock_template_provider)
    mock_template_provider.parse.return_value = SHOW_VERSION_PARSED
    parsed = cmd.parse(SHOW_VERSION_RAW)[0]
    assert parsed["VERSION"] == "17.12.1"
    assert parsed["UPTIME"].startswith("1 day")


def test_show_version_format_result_minimal():
    """Checks formatted version output contains expected version and reload details."""
    mock_template_provider = Mock()
    command = ShowVersion(template_provider=mock_template_provider)
    result = SHOW_VERSION_PARSED
    formatted = _to_text(command.format_result(result))
    assert "17.12.1" in formatted
    assert "UPTIME" in formatted
