# SPDX-License-Identifier: MPL-2.0
from __future__ import annotations


class NetimateError(Exception):
    """Base class for **all** Netimate‑specific exceptions.

    Catch this to handle any user‑facing error in a single place::

        try:
            netimate.run(...)
        except NetimateError as err:
            print(err)
    """

    default_message: str = "An unknown Netimate error occurred."

    def __init__(self, message: str | None = None, *, cause: Exception | None = None) -> None:
        if message is None:
            message = self.default_message
        super().__init__(message)
        # Preserve the original stack if provided
        if cause is not None:
            self.__cause__ = cause
