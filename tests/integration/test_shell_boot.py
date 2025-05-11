# SPDX-License-Identifier: MPL-2.0
import os
import subprocess
import sys


def test_shell_starts_and_exits(temp_device_and_settings_files):
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files
    env = os.environ.copy()
    env["NETIMATE_CONFIG_PATH"] = str(settings_yaml)
    env["NETIMATE_EXTRA_PLUGIN_PACKAGES"] = "tests.fakes"

    result = subprocess.run(
        [sys.executable, "-m", "netimate", "--shell"],
        input="exit\n",
        text=True,
        capture_output=True,
        env=env,
    )

    assert "Welcome to netimate Shell" in result.stdout
    assert "Exiting netimate shell." in result.stdout
