# SPDX-License-Identifier: MPL-2.0
"""
netimate.infrastructure.config_loader
-------------------------------------
Utility for locating and loading a YAML‑based Netimate configuration file,
then returning a concrete `SettingsInterface` implementation that the
application views (Shell/CLI) can consume.
"""
import yaml

from netimate.infrastructure.settings import SettingsImpl
from netimate.infrastructure.utils.file_management import find_file_upward
from netimate.interfaces.infrastructure.settings import SettingsInterface


class ConfigLoader:
    """
    Loads netimate configuration from a YAML file for use in Shell or other views.
    """

    def __init__(self, filename: str):
        """
        Parameters
        ----------
        filename:
            The basename of the YAML configuration file (e.g. ``netimate.yaml``).
            The loader walks upward from the current working directory until it
            finds the file, mirroring Git‑style config discovery.
        Raises
        ------
        FileNotFoundError
            If the file cannot be located in the directory tree.
        """
        self.filepath = find_file_upward(filename)
        if self.filepath is None:
            raise FileNotFoundError(
                f"Configuration file '{filename}' not found in any parent directory."
            )

    def load(self) -> SettingsInterface:
        """Parse YAML and return a `SettingsImpl` instance.

        Raises
        ------
        ValueError
            If required keys are missing from the YAML.
        """

        with open(self.filepath, "r") as f:
            data = yaml.safe_load(f) or {}

        try:
            return SettingsImpl(
                device_repo=data["device_repo"],
                log_level=data["log_level"],
                template_paths=data["template_paths"],
                plugin_configs=data.get("plugin_configs"),
            )
        except KeyError as e:
            raise ValueError(f"Missing required config value: {e}")
