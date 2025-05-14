# SPDX-License-Identifier: MPL-2.0
"""Configuration‑related errors."""

from __future__ import annotations

from .base import NetimateError


class ConfigError(NetimateError):
    """Raised when configuration files are missing, malformed or invalid."""

    default_message = "Configuration error"
