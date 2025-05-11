# SPDX-License-Identifier: MPL-2.0
from netimate.infrastructure.logging import configure_logging
import logging


def test_configure_logging_basic():
    configure_logging("info")
    assert logging.getLogger().level == logging.INFO


def test_configure_logging_verbose():
    configure_logging("debug")
    assert logging.getLogger().level == logging.DEBUG


def test_configure_logging_off():
    configure_logging("off")
    assert logging.getLogger().level == logging.ERROR
