# SPDX-License-Identifier: MPL-2.0
import json
from abc import abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

from rich.table import Table

from netimate.interfaces.infrastructure.template_provider import TemplateProviderInterface
from netimate.interfaces.plugin.plugin import Plugin


class DeviceCommand(Plugin):  # pragma: no cover
    """
    Base class for CLI device‑level commands.

    Key ideas
    ----------
    * A *template provider* (TextFSM, TTP, etc.) is injected by the application layer
      so plugins stay agnostic of template‑loading details.
    * Each concrete command only needs to supply the raw command string and the
      relative template filename; the parsing logic is handled here.
    """

    # Metadata for nicer human‑readable output -------------------------------
    label: str = ""  # Short label used by diagnostics; plugin may override
    table_headers: list[str] | None = None  # Column headers for tabular output

    def __init__(
        self, template_provider: TemplateProviderInterface, plugin_settings: Dict | None = None
    ):
        # Template provider should **always** be present – treat `None` as a bug.
        super().__init__(plugin_settings)
        if template_provider is None:
            raise ValueError("DeviceCommand requires a valid TemplateProviderInterface")
        self._template_provider = template_provider

    # ----- Metadata the concrete command must supply -------------------------
    @abstractmethod
    def command_string(self) -> str:
        """CLI string that should be executed on the network device."""
        ...

    @abstractmethod
    def template_file(self) -> Optional[str] | Path:
        """
        Relative path (from the template search roots) to the TextFSM/TTP template
        used to parse this command's raw output.
        Example: ``"cisco_ios/cisco_ios_show_version.textfsm"``.
        """
        ...

    # ----- Generic parsing / formatting --------------------------------------
    def parse(self, raw_output: str) -> Any:
        """
        Parse *raw_output* using the declared template. Concrete commands usually do
        **not** need to override this – override only when custom post‑processing or
        multi‑template stitching is required.

        Returns
        -------
        Any
            Typically a list[dict] (TextFSM) or dict (TTP) with parsed fields.
        """
        return self._template_provider.parse(self.template_file(), raw_output)

    def summarise_result(self, result: Any) -> str:
        """
        Optional: provide a 1-line summary of parsed results, for diagnostics.
        Defaults to showing the number of entries if not overridden.

        Returns
        -------
        str
            Summary string for quick display (e.g., in a table row).
        """
        if isinstance(result, list):
            return f"{len(result)} entries" if result else "[empty list]"
        if isinstance(result, dict):
            return f"{len(result)} fields" if result else "[empty dict]"
        return str(result)

    # ----- Rich formatting helper -------------------------------------------
    def build_rich(self, result: Any) -> Table | str:
        """
        Convert parsed *result* into a Rich table if ``table_headers`` is set
        and the result is a list[dict]. Fallback to JSON for other shapes.

        Returns
        -------
        str
            Text representation exported from Rich Console (suitable for
            plain‑text terminals).
        """
        if self.table_headers and isinstance(result, list):
            table = Table(show_lines=True)
            for col in self.table_headers:
                table.add_column(col)
            for row in result:
                # Preserve header order; default to str(row.get(...))
                table.add_row(*(str(row.get(h, "")) for h in self.table_headers))
            return table
        # Fallback
        return json.dumps(result, indent=2)

    def format_result(self, result: Any) -> Table | str:
        """
        Human‑readable formatting.
        * If ``table_headers`` is provided and *result* looks like a list[dict],
          render a Rich table.
        * Otherwise, pretty‑print JSON.
        """
        return self.build_rich(result)
