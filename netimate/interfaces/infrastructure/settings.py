# SPDX-License-Identifier: MPL-2.0
"""
netimate.interfaces.settings
----------------------------
Declares :class:`SettingsInterface` – a structural typing contract that
UI layers (CLI / Shell) rely on to fetch runtime configuration.  A concrete
implementation (`SettingsImpl` in ``infrastructure.settings``) is injected
at startup by the composition‑root.
"""
from typing import Dict, Protocol


class SettingsInterface(Protocol):
    """
    Structural interface that describes the user‑visible configuration.

    Implementations must expose:
    • ``device_repo`` – dotted import path of the default DeviceRepository
    • ``log_level``   – current logger level ("off" | "info" | "debug")
    • ``template_paths`` – ordered list of template directories
    • ``plugin_configs`` – arbitrary mapping forwarded to plugin constructors
    """

    @property
    def device_repo(self) -> str: ...

    @property
    def log_level(self) -> str: ...

    @log_level.setter
    def log_level(self, value: str) -> None: ...

    @property
    def template_paths(self) -> list[str]:  # pragma: no cover
        """Ordered list of directories that contain ``*.tmpl`` assets."""
        ...

    @property
    def plugin_configs(self) -> Dict[str, str]: ...
