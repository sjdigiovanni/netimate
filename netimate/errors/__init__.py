"""Top‑level re‑exports for Netimate's custom exception hierarchy."""
from __future__ import annotations

from .base import NetimateError
from .cli import CliUsageError
from .command import CommandError
from .config import ConfigError
from .connection import ConnectionProtocolError, AuthError, ConnectionTimeoutError
from .plugin import PluginError
from .runner import RunnerError
from .shell import ShellRuntimeError

__all__ = [
    "NetimateError",
    "CliUsageError",
    "CommandError",
    "ConfigError",
    "ConnectionProtocolError",
    "AuthError",
    "ConnectionTimeoutError",
    "PluginError",
    "RunnerError",
    "ShellRuntimeError"
]