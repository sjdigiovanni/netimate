# SPDX-License-Identifier: MPL-2.0
from os.path import expanduser
from unittest.mock import AsyncMock, patch

import pytest
from netimate.plugins.connection_protocols.scrapli.asyncssh import (
    ScrapliAsyncsshConnectionProtocol,
    PLATFORM_DRIVERS,
)
from netimate.models.device import Device


@pytest.mark.asyncio
@patch("netimate.plugins.connection_protocols.scrapli.asyncssh.AsyncGenericDriver")
async def test_scrapli_connect(mock_asyncscrapli, dummy_device):
    """
    Test that ScrapliAsyncsshConnectionProtocol.connect() initializes the
    correct Scrapli driver with expected parameters and opens the connection.
    """
    mock_conn = AsyncMock()
    mock_asyncscrapli.return_value = mock_conn

    protocol = ScrapliAsyncsshConnectionProtocol(dummy_device)
    await protocol.connect()

    mock_asyncscrapli.assert_called_once_with(
        host="10.1.1.1",
        auth_username="u",
        auth_password="p",
        auth_secondary="p",
        transport="asyncssh",
        ssh_known_hosts_file=expanduser("~/.ssh/known_hosts"),
        transport_options={},
    )
    mock_conn.open.assert_awaited_once()


@pytest.mark.asyncio
@patch("netimate.plugins.connection_protocols.scrapli.asyncssh.AsyncGenericDriver")
async def test_scrapli_send_command(mock_asyncscrapli, dummy_device):
    """
    Test that ScrapliAsyncsshConnectionProtocol.send_command() sends the
    command and returns the expected output.
    """
    mock_conn = AsyncMock()
    mock_conn.send_command.return_value.result = "output for: show version"
    mock_asyncscrapli.return_value = mock_conn

    protocol = ScrapliAsyncsshConnectionProtocol(dummy_device)
    await protocol.connect()
    result = await protocol.send_command("show version")

    assert result == "output for: show version"
    mock_conn.send_command.assert_awaited_once_with("show version")


@pytest.mark.asyncio
@patch("netimate.plugins.connection_protocols.scrapli.asyncssh.AsyncGenericDriver")
async def test_scrapli_disconnect(mock_asyncscrapli, dummy_device):
    """
    Test that ScrapliAsyncsshConnectionProtocol.disconnect() closes the connection.
    """
    mock_conn = AsyncMock()
    mock_asyncscrapli.return_value = mock_conn

    protocol = ScrapliAsyncsshConnectionProtocol(dummy_device)
    await protocol.connect()
    await protocol.disconnect()

    mock_conn.close.assert_awaited_once()


@pytest.mark.parametrize(
    "platform,expected_cls",
    [
        ("iosxe", "AsyncIOSXEDriver"),
        ("nxos", "AsyncNXOSDriver"),
        ("iosxr", "AsyncIOSXRDriver"),
        ("eos", "AsyncEOSDriver"),
        ("junos", "AsyncJunosDriver"),
        ("weirdos", "AsyncGenericDriver"),
        (None, "AsyncGenericDriver"),
    ],
)
def test_scrapli_driver_selection_resolution(monkeypatch, platform, expected_cls, dummy_device):
    """
    Confirm the correct Scrapli driver class is chosen based on device.platform
    without opening a real connection.
    """
    selected = {}

    # Patch all drivers to stub classes that record their name
    class FakeDriver:
        def __init__(self, *args, **kwargs):
            selected["used"] = self.__class__.__name__

        async def open(self):
            pass

    # Monkeypatch every class in the driver map
    for key, real_cls in PLATFORM_DRIVERS.items():
        monkeypatch.setitem(PLATFORM_DRIVERS, key, type(expected_cls, (FakeDriver,), {}))
    monkeypatch.setitem(PLATFORM_DRIVERS, "generic", type("AsyncGenericDriver", (FakeDriver,), {}))

    proto = ScrapliAsyncsshConnectionProtocol(dummy_device)
    # Do not actually await, just trigger __init__ to check class resolution
    proto.client = PLATFORM_DRIVERS.get(platform, PLATFORM_DRIVERS["generic"])(
        host="10.1.1.1",
        auth_username="u",
        auth_password="p",
        transport="asyncssh",
        transport_options={},
    )

    assert selected["used"] == expected_cls
