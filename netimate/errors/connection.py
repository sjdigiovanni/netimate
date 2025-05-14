# SPDX-License-Identifier: MPL-2.0
"""Connection‑level errors (SSH, Telnet, NETCONF, etc.)."""

from __future__ import annotations

from .base import NetimateError


class ConnectionProtocolError(NetimateError):
    """General transport or session failure."""

    default_message = "Connection to device failed"


class AuthError(ConnectionProtocolError):
    """Authentication failure."""

    default_message = "Authentication failed"


class ConnectionTimeoutError(ConnectionProtocolError):
    """Operation timed out."""

    default_message = "Connection timed out"
