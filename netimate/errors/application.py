# netimate/errors/application.py
from .base import NetimateError


class ApplicationError(NetimateError):
    """Raised when the application layer cannot fulfil a user request."""

    default_message = "Application-level failure"
