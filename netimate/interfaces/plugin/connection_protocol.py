# SPDX-License-Identifier: MPL-2.0
"""
netimate.interfaces.plugin.connection_protocol
----------------------------------------------
Abstract base plugin class for any interactive connection mechanism
(SSH, Telnet, NETCONF, RESTCONF, Fake‑Async for tests, etc.).  Concrete
implementations are loaded at runtime by the PluginRegistry and used by
the Runner to execute device commands.
"""
import inspect
from abc import abstractmethod
from functools import wraps
from typing import Dict

from netimate.errors import ConnectionProtocolError, NetimateError
from netimate.interfaces.plugin.plugin import Plugin
from netimate.models.device import Device


def _wrap_netimate_errors(fn):
    """
    Ensure only NetimateError (or subclasses) exit the function.

    Any other exception is wrapped in ConnectionProtocolError so that layers
    above ConnectionProtocol never see third‑party tracebacks.
    """
    if inspect.iscoroutinefunction(fn):

        @wraps(fn)
        async def async_wrapper(*args, **kwargs):
            try:
                return await fn(*args, **kwargs)
            except NetimateError:
                raise
            except Exception as err:  # pylint: disable=broad-except
                raise ConnectionProtocolError("Unhandled protocol error") from err

        return async_wrapper
    else:

        @wraps(fn)
        def sync_wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except NetimateError:
                raise
            except Exception as err:  # pylint: disable=broad-except
                raise ConnectionProtocolError("Unhandled protocol error") from err

        return sync_wrapper


class ConnectionProtocol(Plugin):  # pragma: no cover
    """
    Base class for all connection‑oriented plugins.

    Contract
    --------
    * ``connect``, ``send_command`` and ``disconnect`` must raise only
      :class:`netimate.errors.NetimateError` (or subclasses) on failure.
    * Any other exception will be wrapped automatically in
      :class:`netimate.errors.ConnectionProtocolError` at runtime (enforced
      via ``__init_subclass__``).

    Lifecycle
    ---------
    1. ``connect``     – open transport / login
    2. ``send_command`` – execute a single command string
    3. ``disconnect``  – cleanly close the session
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Automatically wrap core public methods so subclasses can't leak
        # external exceptions.
        for _name in ("connect", "send_command", "disconnect"):
            if hasattr(cls, _name):
                setattr(cls, _name, _wrap_netimate_errors(getattr(cls, _name)))

    @abstractmethod
    def __init__(self, device: Device, plugin_settings: Dict | None = None):
        """
        Parameters
        ----------
        device:
            Concrete :class:`netimate.models.device.Device` the protocol will
            talk to (holds IP, port, credentials).
        plugin_settings:
            Optional plugin‑specific configuration block from
            ``settings.plugin_configs``; may be ``None``.
        """
        super().__init__(plugin_settings)
        self.device = device

    @abstractmethod
    async def connect(self) -> None:
        """Open the underlying transport channel."""

    @abstractmethod
    async def send_command(self, command: str) -> str:
        """Run *command* and return raw screen string."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the transport and free resources."""
