# SPDX-License-Identifier: MPL-2.0
"""
netimate.plugins.device_repositories.netbox
-------------------------------------------
Device repository plugin that uses the Netbox API to retrieve device information.
This plugin serves as a transition adapter between Netbox's data model and Netimate's Device model.
"""
import logging
import os
from typing import Dict, List

import netbox

from netimate.interfaces.plugin.device_repository import DeviceRepository
from netimate.models.device import Device

logger = logging.getLogger(__name__)


class NetboxDeviceRepository(DeviceRepository):
    """
    Device repository that retrieves device information from Netbox.
    
    This plugin connects to a Netbox instance using the pynetbox library and
    maps Netbox device data to Netimate Device objects.
    """
    
    def __init__(self, plugin_settings: Dict):
        """
        Initialize the Netbox device repository.
        
        Parameters
        ----------
        plugin_settings:
            Dictionary containing Netbox connection settings:
            - url: Netbox API URL (required)
            - token: Netbox API token (required)
            - ssl_verify: Whether to verify SSL certificates (optional, default: True)
            - default_protocol: Default protocol to use for devices (optional, default: "ssh")
            - default_username: Default username for device connections (optional)
            - default_password: Default password for device connections (optional)
        """
        super().__init__(plugin_settings)
        if not self.plugin_settings:
            raise ValueError("Settings file missing netbox config!")
        
        required_settings = ["url", "token"]
        for setting in required_settings:
            if not self.plugin_settings.get(setting):
                raise ValueError(f"Settings file missing netbox.{setting}!")
        
        self._url = self.plugin_settings["url"]
        self._token = self.plugin_settings["token"]
        self._ssl_verify = self.plugin_settings.get("ssl_verify", True)
        self._default_protocol = self.plugin_settings.get("default_protocol", "ssh")
        self._default_username = self.plugin_settings.get("default_username")
        self._default_password = self.plugin_settings.get("default_password") or os.getenv("NETIMATE_NETBOX_PASSWORD")
        
        # Initialize the pynetbox API client
        self._nb = netbox.api(
            url=self._url,
            token=self._token,
            ssl_verify=self._ssl_verify
        )
    
    @staticmethod
    def plugin_name() -> str:
        """Return the registry key that identifies this plugin."""
        return "netbox"
    
    def list_devices(self) -> List[Device]:
        """
        List all available devices from Netbox.
        
        Returns
        -------
        List[Device]
            List of Device objects representing network devices in Netbox.
        """
        logger.info(f"Loading devices from Netbox: {self._url}")
        
        # Get all devices from Netbox
        netbox_devices = self._nb.dcim.devices.all()
        
        devices = []
        for nb_device in netbox_devices:
            # Skip devices that are not active
            if not nb_device.status or nb_device.status.value != "active":
                continue
                
            # Skip devices without a primary IP
            if not nb_device.primary_ip:
                logger.warning(f"Skipping device {nb_device.name} - no primary IP")
                continue
            
            # Get platform information
            platform = "unknown"
            if nb_device.platform:
                platform = nb_device.platform.slug
            
            # Get site information
            site = None
            if nb_device.site:
                site = nb_device.site.name
            
            # Create Device object
            device = Device(
                name=nb_device.name,
                host=str(nb_device.primary_ip.address).split("/")[0],  # Remove CIDR notation
                username=self._default_username or "",
                password=self._default_password or "",
                protocol=self._default_protocol,
                platform=platform,
                site=site
            )
            
            devices.append(device)
        
        logger.debug(f"Loaded {len(devices)} devices from Netbox")
        return devices