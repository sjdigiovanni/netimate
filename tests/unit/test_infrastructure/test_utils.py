# SPDX-License-Identifier: MPL-2.0
import os

import pytest

from netimate.infrastructure.utils.file_management import find_file_upward


def test_find_file_upward_happy_path(tmp_path):
    nested_dir = tmp_path / "a" / "b" / "c"
    nested_dir.mkdir(parents=True)

    config_file = tmp_path / "settings.yaml"
    config_file.write_text("dummy: true")

    old_cwd = os.getcwd()
    os.chdir(nested_dir)

    try:
        found = find_file_upward("settings.yaml")
        assert found == config_file
    finally:
        os.chdir(old_cwd)


def test_find_file_upward_not_found(tmp_path):
    nested_dir = tmp_path / "a" / "b"
    nested_dir.mkdir(parents=True)

    old_cwd = os.getcwd()
    os.chdir(nested_dir)

    try:
        with pytest.raises(FileNotFoundError, match="Could not find 'settings.yaml'"):
            find_file_upward("settings.yaml")
    finally:
        os.chdir(old_cwd)
