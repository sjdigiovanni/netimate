# SPDX-License-Identifier: MPL-2.0
from .base import NetimateError


class ApplicationError(NetimateError):
    """Raised when the application layer cannot fulfil a user request."""

    default_message = "Application-level failure"
