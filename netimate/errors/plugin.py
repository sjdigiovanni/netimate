"""Plugin discovery and loading errors."""

from __future__ import annotations

from .base import NetimateError


class PluginError(NetimateError):
    """Raised when a plugin cannot be found, loaded or initialised."""

    default_message = "Plugin system error"
