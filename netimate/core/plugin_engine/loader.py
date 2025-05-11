# SPDX-License-Identifier: MPL-2.0
"""
netimate.core.plugin_engine.loader
----------------------------------
Runtime discovery utility that walks a list of package roots, dynamically
imports Python modules, and returns every concrete subclass of the given
*interface* (base class).  Used by PluginRegistrar to automatically load
DeviceCommand, ConnectionProtocol, and DeviceRepository plugins supplied
either in the built‑in packages or via the NETIMATE_EXTRA_PLUGIN_PACKAGES
environment variable.
"""

import importlib
import inspect
import logging
from pathlib import Path
from types import ModuleType
from typing import List, Type, cast

logger = logging.getLogger(__name__)


class PluginLoader:
    """Discover subclasses of *interface* inside each package root given."""

    def __init__(self, base_paths: List[str] | str, interface: Type):
        """
        Parameters
        ----------
        base_paths:
            One or multiple dotted‑package roots to scan.  Example:
            ``"netimate.plugins.device_commands"``.
        interface:
            Abstract base class that discovered classes must inherit from.
        """
        if isinstance(base_paths, str):
            base_paths = [base_paths]  # ← wrap single string
        self.base_paths = base_paths
        self.interface = interface

    def _scan_package(self, pkg_name: str, discovered: list[Type]):
        """Import *pkg_name* and recursively scan `.py` files under it.

        Any subclass of *self.interface* that is not the interface itself is
        appended to *discovered*.
        """
        try:
            root_mod: ModuleType = importlib.import_module(pkg_name)
        except ImportError as exc:
            logger.warning("Plugin root import failed '%s': %s", pkg_name, exc)
            return

        pkg_path = Path(cast(str, root_mod.__file__)).parent
        for file in pkg_path.rglob("*.py"):
            if file.name == "__init__.py":
                continue

            rel_path = file.relative_to(pkg_path).with_suffix("")
            module_name = f"{pkg_name}.{'.'.join(rel_path.parts)}"
            logger.debug("Scanning module: %s", module_name)

            try:
                module = importlib.import_module(module_name)
            except Exception as exc:
                logger.warning("Failed to import %s: %s", module_name, exc)
                continue

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, self.interface) and obj is not self.interface:
                    logger.info("Discovered plugin: %s in %s", obj.__name__, module_name)
                    discovered.append(obj)

    def discover(self) -> list[Type]:
        """Return a list of all plugin classes discovered in *base_paths*."""
        discovered: list[Type] = []
        for pkg in self.base_paths:
            self._scan_package(pkg, discovered)
        return discovered
