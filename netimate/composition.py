# SPDX-License-Identifier: MPL-2.0
"""
netimate.composition.composition_root
-------------------------------------
Manual dependency‑injection container (a.k.a. composition root).

Responsibilities:
1. Load user settings from YAML.
2. Configure global logging.
3. Build an in‑memory PluginRegistry and auto‑register built‑in + extra plugins.
4. Instantiate core services (TemplateProvider, Runner).
5. Return an :class:`ApplicationInterface` ready for consumption by CLI/Shell.

Keeping this wiring in one place ensures other modules stay free of import‑time
side‑effects and simplifies future refactoring to an IoC/DI framework.
"""

import os

from netimate.application.application import Application
from netimate.core.plugin_engine.plugin_registry import PluginKind, PluginRegistry
from netimate.core.plugin_engine.registrar import PluginRegistrar
from netimate.core.runner import Runner
from netimate.infrastructure.config_loader import ConfigLoader
from netimate.infrastructure.logging import configure_logging
from netimate.infrastructure.template_provider.filesystem import FileSystemTemplateProvider
from netimate.interfaces.application.application import ApplicationInterface
from netimate.interfaces.plugin.connection_protocol import ConnectionProtocol
from netimate.interfaces.plugin.device_command import DeviceCommand
from netimate.interfaces.plugin.device_repository import DeviceRepository


def composition_root() -> ApplicationInterface:
    """Compose and return a ready‑to‑use :class:`ApplicationInterface`.

    Returns
    -------
    ApplicationInterface
        Fully initialised application façade injected with:
        * Settings          – parsed from YAML via ConfigLoader.
        * Template provider – FileSystemTemplateProvider for TextFSM/TTP.
        * Runner            – asynchronous execution engine.
        * Plugin registry   – populated with built‑in & extra plugins.
    """
    # 1. Load settings
    config_loader = ConfigLoader(os.getenv("NETIMATE_CONFIG_PATH", "settings.yaml"))
    settings = config_loader.load()

    # 2. Configure logging
    configure_logging(settings.log_level)

    # 3. Register plugins
    registry = PluginRegistry()
    registrar = PluginRegistrar(registry)

    registrar.register_plugins(
        PluginKind.DEVICE_COMMAND, "netimate.plugins.device_commands", DeviceCommand
    )
    registrar.register_plugins(
        PluginKind.PROTOCOL, "netimate.plugins.connection_protocols", ConnectionProtocol
    )
    registrar.register_plugins(
        PluginKind.REPOSITORY, "netimate.plugins.device_repositories", DeviceRepository
    )

    # 3. Create dependencies
    template_provider = FileSystemTemplateProvider(settings.template_paths)
    runner = Runner(registry, settings.plugin_configs)

    # 4. Initialise application
    app = Application(registry, settings, runner, template_provider)

    return app
