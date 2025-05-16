# SPDX-License-Identifier: MPL-2.0
import os
import subprocess
import sys


def test_cli_happy_path(temp_device_and_settings_files):
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files
    env = os.environ.copy()
    env["NETIMATE_CONFIG_PATH"] = str(settings_yaml)
    env["NETIMATE_EXTRA_PLUGIN_PACKAGES"] = "tests.fakes"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "netimate",
            "--device-names",
            "r1",
            "--command",
            "echo-test",
        ],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )

    assert "---\n[r1]\n{'raw': 'echo test'}\n" in result.stdout
