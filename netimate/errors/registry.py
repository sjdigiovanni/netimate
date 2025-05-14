# SPDX-License-Identifier: MPL-2.0
"""Plugin discovery and loading errors."""

from __future__ import annotations

from .base import NetimateError


class RegistryError(NetimateError):
    """Raised when a plugin cannot be found, loaded or initialised."""

    default_message = "Plugin system error"
