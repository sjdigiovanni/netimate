# SPDX-License-Identifier: MPL-2.0
from __future__ import annotations

from .base import NetimateError


class ShellRuntimeError(NetimateError):
    """Raised when a command entered the interactive shell fails at runtime."""

    default_message = "Shell command failed"
