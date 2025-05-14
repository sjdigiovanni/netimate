# SPDX-License-Identifier: MPL-2.0
from unittest.mock import MagicMock, patch

import pytest
from netmiko import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)

from netimate.errors import (
    AuthError,
    ConnectionProtocolError,
    ConnectionTimeoutError,
)
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


@patch("netimate.plugins.connection_protocols.netmiko.telnet.ConnectHandler")
@pytest.mark.asyncio
async def test_telnet_auth_failure_raises_auth_error(mock_connect, dummy_device):
    mock_connect.side_effect = NetmikoAuthenticationException("bad creds")
    protocol = NetmikoTelnetConnectionProtocol(dummy_device)

    with pytest.raises(AuthError):
        await protocol.connect()


@patch("netimate.plugins.connection_protocols.netmiko.telnet.ConnectHandler")
@pytest.mark.asyncio
async def test_telnet_timeout_raises_timeout_error(mock_connect, dummy_device):
    mock_connect.side_effect = NetmikoTimeoutException("timeout")
    protocol = NetmikoTelnetConnectionProtocol(dummy_device)

    with pytest.raises(ConnectionTimeoutError):
        await protocol.connect()


@patch("netimate.plugins.connection_protocols.netmiko.telnet.ConnectHandler")
@pytest.mark.asyncio
async def test_telnet_unexpected_exception_is_wrapped(mock_connect, dummy_device):
    mock_connect.side_effect = RuntimeError("boom")
    protocol = NetmikoTelnetConnectionProtocol(dummy_device)

    with pytest.raises(ConnectionProtocolError):
        await protocol.connect()
