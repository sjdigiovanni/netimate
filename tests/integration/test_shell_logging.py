# SPDX-License-Identifier: MPL-2.0
import subprocess
import sys
import os


def test_shell_verbose_toggle(temp_device_and_settings_files):
    devices, temp_devices_path, settings_yaml = temp_device_and_settings_files
    env = os.environ.copy()
    env["NETIMATE_CONFIG_PATH"] = str(settings_yaml)
    env["NETIMATE_EXTRA_PLUGIN_PACKAGES"] = "tests.fakes"

    result = subprocess.run(
        [sys.executable, "-m", "netimate", "--shell"],
        input="log_level info\nexit\n",
        text=True,
        capture_output=True,
        env=env,
    )

    assert "Switched log level to info" in result.stdout
