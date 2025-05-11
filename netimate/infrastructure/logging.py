# SPDX-License-Identifier: MPL-2.0
"""
netimate.infrastructure.logging
-------------------------------
Centralised logging configuration helper.  Converts the string log‑level
option from settings into a root logger configuration and installs a single
stream handler with a consistent format.
"""
import logging


def configure_logging(log_level: str):
    """Configure root logger according to *log_level*.

    Parameters
    ----------
    log_level:
        One of ``"off"``, ``"info"``, or ``"debug"`` (case‑sensitive).

    Raises
    ------
    ValueError
        If *log_level* is not one of the accepted values.
    """
    if log_level == "off":
        level = logging.ERROR
    elif log_level == "info":
        level = logging.INFO
    elif log_level == "debug":
        level = logging.DEBUG
    else:
        raise ValueError("Invalid log level provided. Options are [off, info, debug]")

    root_logger = logging.getLogger()
    # Clear any existing handlers (prevents duplicates)
    root_logger.handlers.clear()

    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(name)s: %(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(level)

    root_logger.setLevel(level)
    root_logger.addHandler(handler)
