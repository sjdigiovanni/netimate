# SPDX-License-Identifier: MPL-2.0
import pytest
from netimate.view.shell.parsers import parse_run_syntax


def test_parse_run_syntax_basic():
    cmd = "show-version on R1"
    command, devices = parse_run_syntax(cmd)
    assert command == "show-version"
    assert devices == ["R1"]


def test_parse_run_syntax_with_runner():
    cmd = "show-version on R1, R2"
    command, devices = parse_run_syntax(cmd)
    assert command == "show-version"
    assert devices == ["R1", "R2"]


def test_parse_run_syntax_invalid():
    with pytest.raises(ValueError):
        parse_run_syntax("invalid syntax")
