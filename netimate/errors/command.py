# SPDX-License-Identifier: MPL-2.0
"""Errors related to executing device commands."""

from __future__ import annotations

from .base import NetimateError


class CommandError(NetimateError):
    """Raised when a device command cannot be executed or parsed."""

    default_message = "Failed to execute command on device"
