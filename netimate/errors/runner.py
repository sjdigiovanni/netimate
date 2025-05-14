# SPDX-License-Identifier: MPL-2.0
"""High‑level runner / orchestration errors."""

from __future__ import annotations

from .base import NetimateError


class RunnerError(NetimateError):
    """Raised when multi‑device orchestration fails."""

    default_message = "Runner failed to complete task"
