# SPDX-License-Identifier: MPL-2.0
"""Infrastructure-layer abstraction for loading text templates used by
command parsers.  Keeping this behind an interface means core/​plugin code can
parse outputs without caring *where* templates live (file-system, package
resources, HTTP, S3, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List


class TemplateProviderInterface(ABC):  # pragma: no cover
    """Thin contract for locating/reading parsing templates."""

    @abstractmethod
    def _get(self, name: str) -> str:
        """Return raw template text for *name* (e.g. ``"iosxe/show_version.tmpl"``).

        Raises:
            FileNotFoundError: if the template cannot be located.
        """
        ...

    @abstractmethod
    def parse(self, template_path: str | Path | None, raw_output: str) -> Any:
        """Return structured data parsed with *template_path*.

        Implementations may return list/ dict/ str depending on template type.
        Fallback behaviour (e.g. if required parsing library is absent) should
        be to return *raw_output* unchanged.
        """
        ...

    @abstractmethod
    def exists(self, name: str) -> bool:
        """Cheap test whether a template is available (does **not** load it)."""
        ...

    @abstractmethod
    def list_templates(self) -> List[str]:
        """Iterate over all known template names.

        Args:
            prefix: optional string to restrict results (e.g. ``"iosxe/"``).
        """
        ...
