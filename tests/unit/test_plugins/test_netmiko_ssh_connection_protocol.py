# SPDX-License-Identifier: MPL-2.0
from unittest.mock import MagicMock, patch

import pytest

from netimate.models.device import Device
from netimate.plugins.connection_protocols.netmiko.ssh import NetmikoSSHConnectionProtocol


@pytest.mark.asyncio
@patch("netimate.plugins.connection_protocols.netmiko.ssh.ConnectHandler")
async def test_ssh_protocol_runs_command(mock_connect_handler):
    """Test that SSH protocol connects and sends a command correctly."""
    mock_connection = MagicMock()
    mock_connection.send_command.return_value = "mocked output"
    mock_connect_handler.return_value = mock_connection

    device = Device(
        name="router1",
        host="10.0.0.1",
        username="admin",
        password="admin",
        protocol="ssh",
        platform="fake",
    )
    protocol = NetmikoSSHConnectionProtocol(device)

    await protocol.connect()
    output = await protocol.send_command("show version")
    await protocol.disconnect()

    assert output == "mocked output"
    mock_connection.send_command.assert_called_once_with("show version")
    mock_connection.disconnect.assert_called_once()
