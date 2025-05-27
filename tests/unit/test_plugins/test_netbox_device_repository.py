# SPDX-License-Identifier: MPL-2.0
"""
Tests for the Netbox device repository plugin.
"""
import os
import unittest
from unittest.mock import MagicMock, patch

import pytest
import pynetbox

from netimate.plugins.device_repositories.netbox import NetboxDeviceRepository
from netimate.models.device import Device


class TestNetboxDeviceRepository(unittest.TestCase):
    """Test cases for the NetboxDeviceRepository class."""

    def setUp(self):
        """Set up test fixtures."""
        self.settings = {
            "url": "http://netbox.example.com",
            "token": "abc123",
            "ssl_verify": False,
            "default_protocol": "ssh",
            "default_username": "admin",
            "default_password": "password"
        }

    @patch("pynetbox.api")
    def test_init(self, mock_api):
        """Test initialization of NetboxDeviceRepository."""
        # Setup mock
        mock_api.return_value = MagicMock()
        
        # Create repository
        repo = NetboxDeviceRepository(self.settings)
        
        # Verify pynetbox.api was called with correct arguments
        mock_api.assert_called_once_with(
            url=self.settings["url"],
            token=self.settings["token"],
            ssl_verify=self.settings["ssl_verify"]
        )
        
        # Verify attributes were set correctly
        self.assertEqual(repo._url, self.settings["url"])
        self.assertEqual(repo._token, self.settings["token"])
        self.assertEqual(repo._ssl_verify, self.settings["ssl_verify"])
        self.assertEqual(repo._default_protocol, self.settings["default_protocol"])
        self.assertEqual(repo._default_username, self.settings["default_username"])
        self.assertEqual(repo._default_password, self.settings["default_password"])

    def test_init_missing_settings(self):
        """Test initialization with missing settings."""
        # Test with None settings
        with self.assertRaises(ValueError):
            NetboxDeviceRepository(None)
        
        # Test with empty settings
        with self.assertRaises(ValueError):
            NetboxDeviceRepository({})
        
        # Test with missing url
        with self.assertRaises(ValueError):
            NetboxDeviceRepository({"token": "abc123"})
        
        # Test with missing token
        with self.assertRaises(ValueError):
            NetboxDeviceRepository({"url": "http://netbox.example.com"})

    @patch("pynetbox.api")
    def test_init_with_env_password(self, mock_api):
        """Test initialization with password from environment variable."""
        # Setup mock and environment
        mock_api.return_value = MagicMock()
        os.environ["NETIMATE_NETBOX_PASSWORD"] = "env_password"
        
        # Create repository with no password in settings
        settings_no_password = self.settings.copy()
        del settings_no_password["default_password"]
        repo = NetboxDeviceRepository(settings_no_password)
        
        # Verify password was taken from environment
        self.assertEqual(repo._default_password, "env_password")
        
        # Clean up
        del os.environ["NETIMATE_NETBOX_PASSWORD"]

    def test_plugin_name(self):
        """Test plugin_name static method."""
        self.assertEqual(NetboxDeviceRepository.plugin_name(), "netbox")

    @patch("pynetbox.api")
    def test_list_devices_empty(self, mock_api):
        """Test list_devices with no devices."""
        # Setup mock
        mock_nb = MagicMock()
        mock_nb.dcim.devices.all.return_value = []
        mock_api.return_value = mock_nb
        
        # Create repository and list devices
        repo = NetboxDeviceRepository(self.settings)
        devices = repo.list_devices()
        
        # Verify results
        self.assertEqual(len(devices), 0)
        mock_nb.dcim.devices.all.assert_called_once()

    @patch("pynetbox.api")
    def test_list_devices(self, mock_api):
        """Test list_devices with sample devices."""
        # Setup mock devices
        mock_device1 = MagicMock()
        mock_device1.name = "router1"
        mock_device1.status.value = "active"
        mock_device1.primary_ip.address = "192.168.1.1/24"
        mock_device1.platform.slug = "ios-xe"
        mock_device1.site.name = "Datacenter"
        
        mock_device2 = MagicMock()
        mock_device2.name = "switch1"
        mock_device2.status.value = "active"
        mock_device2.primary_ip.address = "192.168.1.2/24"
        mock_device2.platform.slug = "ios"
        mock_device2.site.name = "Datacenter"
        
        # Device with no status (should be skipped)
        mock_device3 = MagicMock()
        mock_device3.name = "inactive-device"
        mock_device3.status = None
        
        # Device with inactive status (should be skipped)
        mock_device4 = MagicMock()
        mock_device4.name = "planned-device"
        mock_device4.status.value = "planned"
        
        # Device with no primary IP (should be skipped)
        mock_device5 = MagicMock()
        mock_device5.name = "no-ip-device"
        mock_device5.status.value = "active"
        mock_device5.primary_ip = None
        
        # Setup mock API
        mock_nb = MagicMock()
        mock_nb.dcim.devices.all.return_value = [
            mock_device1, mock_device2, mock_device3, mock_device4, mock_device5
        ]
        mock_api.return_value = mock_nb
        
        # Create repository and list devices
        repo = NetboxDeviceRepository(self.settings)
        devices = repo.list_devices()
        
        # Verify results
        self.assertEqual(len(devices), 2)  # Only 2 active devices with IPs
        
        # Check first device
        self.assertEqual(devices[0].name, "router1")
        self.assertEqual(devices[0].host, "192.168.1.1")  # CIDR notation removed
        self.assertEqual(devices[0].username, self.settings["default_username"])
        self.assertEqual(devices[0].password, self.settings["default_password"])
        self.assertEqual(devices[0].protocol, self.settings["default_protocol"])
        self.assertEqual(devices[0].platform, "ios-xe")
        self.assertEqual(devices[0].site, "Datacenter")
        
        # Check second device
        self.assertEqual(devices[1].name, "switch1")
        self.assertEqual(devices[1].host, "192.168.1.2")  # CIDR notation removed
        self.assertEqual(devices[1].platform, "ios")


if __name__ == "__main__":
    unittest.main()