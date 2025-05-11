# SPDX-License-Identifier: MPL-2.0
import pytest
from unittest.mock import patch, MagicMock
from netimate.plugins.connection_protocols.netmiko.telnet import NetmikoTelnetConnectionProtocol


@patch("netimate.plugins.connection_protocols.netmiko.telnet.ConnectHandler")
@pytest.mark.asyncio
async def test_telnet_connect(mock_connect, dummy_device):
    """Test that NetmikoTelnetConnectionProtocol.connect correctly calls ConnectHandler."""
    protocol = NetmikoTelnetConnectionProtocol(dummy_device)
    await protocol.connect()

    mock_connect.assert_called_once_with(
        device_type="cisco_ios_telnet", host="10.1.1.1", username="u", password="p"
    )


@patch("netimate.plugins.connection_protocols.netmiko.telnet.ConnectHandler")
@pytest.mark.asyncio
async def test_telnet_send_command(mock_connect, dummy_device):
    """
    Test sending a command using NetmikoTelnetConnectionProtocol and receiving expected output.
    """
    mock_conn = MagicMock()
    mock_conn.send_command.return_value = "OK"
    mock_connect.return_value = mock_conn

    protocol = NetmikoTelnetConnectionProtocol(dummy_device)
    await protocol.connect()

    output = await protocol.send_command("show version")
    assert output == "OK"
    mock_conn.send_command.assert_called_with("show version")


@patch("netimate.plugins.connection_protocols.netmiko.telnet.ConnectHandler")
@pytest.mark.asyncio
async def test_telnet_disconnect(mock_connect, dummy_device):
    """Test that disconnect properly closes the NetmikoTelnetConnectionProtocol connection."""
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    protocol = NetmikoTelnetConnectionProtocol(dummy_device)
    await protocol.connect()
    await protocol.disconnect()

    mock_conn.disconnect.assert_called_once()
