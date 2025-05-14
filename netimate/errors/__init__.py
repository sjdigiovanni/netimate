# SPDX-License-Identifier: MPL-2.0
"""Top‑level re‑exports for Netimate's custom exception hierarchy."""

from __future__ import annotations

from .application import ApplicationError
from .base import NetimateError
from .cli import CliUsageError
from .command import CommandError
from .config import ConfigError
from .connection import AuthError, ConnectionProtocolError, ConnectionTimeoutError
from .registry import RegistryError
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
    "RegistryError",
    "RunnerError",
    "ShellRuntimeError",
    "ApplicationError",
]
