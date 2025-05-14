"""CLI‑specific usage errors."""

from __future__ import annotations

from .base import NetimateError


class CliUsageError(NetimateError):
    """Raised for incorrect CLI invocation (invalid flags, arguments, etc.)."""

    default_message = "Invalid CLI usage"
