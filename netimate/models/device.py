# SPDX-License-Identifier: MPL-2.0
"""
netimate.models.device
----------------------
Simple dataclass representing a managed network device.  Instances are
created by DeviceRepository plugins and consumed by the Runner and
ConnectionProtocol plugins.
"""

from dataclasses import dataclass


@dataclass
class Device:
    """Dataclass holding connection metadata for a single device."""

    name: str
    host: str
    username: str
    password: str
    protocol: str
    platform: str
    site: str | None = None
