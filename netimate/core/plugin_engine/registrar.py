# SPDX-License-Identifier: MPL-2.0
"""
netimate.core.plugin_engine.registrar
-------------------------------------
Binds the discovery layer (PluginLoader) to the in‑memory PluginRegistry.
It resolves the list of package roots to scan based on the built‑in
*base_path* plus any additional roots provided via the
``NETIMATE_EXTRA_PLUGIN_PACKAGES`` environment variable.
"""

import logging
import os
from typing import Type

from netimate.core.plugin_engine.loader import PluginLoader
from netimate.core.plugin_engine.plugin_registry import PluginKind, PluginRegistry

logger = logging.getLogger(__name__)


class PluginRegistrar:
    def __init__(self, registry: PluginRegistry):
        self.registry = registry

    def register_plugins(self, kind: PluginKind, base_path: str, interface: Type):
        """Discover and register all plugins of *kind* found under *base_path*.

        Extra packages can be supplied at runtime by setting the environment
        variable ``NETIMATE_EXTRA_PLUGIN_PACKAGES`` to a colon‑separated list
        of dotted package names.
        """
        extra_pkgs = os.getenv("NETIMATE_EXTRA_PLUGIN_PACKAGES", "").split(":")
        pkgs = [base_path, *filter(None, extra_pkgs)]
        loader = PluginLoader(pkgs, interface)
        discovered = loader.discover()

        for plugin in discovered:
            logger.info(f"Registering {kind.value} plugin: {plugin.plugin_name()}")
            self.registry.register(kind, plugin.plugin_name(), plugin)

        logger.info(f"Registered {len(discovered)} {kind.value}(s) from {base_path}")
