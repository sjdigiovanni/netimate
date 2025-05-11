# SPDX-License-Identifier: MPL-2.0
from __future__ import annotations

import logging
from functools import lru_cache
from io import StringIO
from pathlib import Path
from typing import List

import textfsm
from ttp import ttp

from netimate.interfaces.infrastructure.template_provider import (
    TemplateProviderInterface,
)

logger = logging.getLogger(__name__)


class FileSystemTemplateProvider(TemplateProviderInterface):
    """Load ``*.tmpl`` files from one or more directories.

    * Search order respects the order of *search_paths*.
    * Results are cached in-memory (LRU) for speed.
    """

    def __init__(self, search_paths: List[str]):
        logger.debug("Initialising FileSystemTemplateProvider with search paths: %s", search_paths)
        self._roots: list[Path] = [Path(p).expanduser().resolve() for p in search_paths]

    @lru_cache(maxsize=128)
    def _read(self, abs_path: Path) -> str:
        # Separate helper so @lru_cache works with Path arg.
        return abs_path.read_text(encoding="utf-8")

    def _get(self, name: str | Path) -> str:
        for root in self._roots:
            candidate = root / name
            if candidate.is_file():
                logger.debug("Template resolved: %s", candidate)
                return self._read(candidate)
        logger.warning("Template '%s' not found in any configured search paths", name)
        raise FileNotFoundError(
            f"Template '{name}' not found in search paths: {', '.join(map(str, self._roots))}"
        )

    def parse(self, template_path: str | Path | None, raw_output: str):
        """
        Very lightweight parser dispatcher.

        * ``*.textfsm`` -> Uses `textfsm` if available, else returns list of rows.
        * ``*.ttp``     -> Uses `ttp` if available, else returns raw_output.
        * other         -> Returns raw_output unchanged.
        """
        if not template_path:
            return

        logger.debug("Parsing output using template '%s'", template_path)
        template_path_obj = Path(template_path)
        suffix = template_path_obj.suffix.lower()
        logger.debug(f"Suffix is {suffix}")

        template = self._get(template_path)
        try:
            if suffix == ".textfsm":
                fsm = textfsm.TextFSM(StringIO(template))
                headers = fsm.header
                rows = fsm.ParseText(raw_output)
                logger.debug("Parsed %d records using %s", len(rows), suffix)
                return [dict(zip(headers, r)) for r in rows]

            elif suffix == ".ttp":
                logger.debug(f"Suffix is {suffix}, running .ttp block")
                parser = ttp(raw_output, template)
                parser.parse()
                logger.debug(
                    "Parsed %d records using %s",
                    len(parser.result(structure="flat_list")[0]),
                    suffix,
                )
                return parser.result(structure="flat_list")[0]

        except ModuleNotFoundError as e:
            logger.error("Optional parsing library missing (%s). Returning raw text.", e)
            # Optional deps not installed – fall through to raw text.

        logger.debug("Returning raw output (no parsing performed)")
        # Fallback: return raw text (so caller still gets something useful)
        return raw_output

    def exists(self, name: str) -> bool:
        """Return ``True`` if *name* exists in any configured search root."""
        return any((root / name).is_file() for root in self._roots)

    def list_templates(self) -> List[str]:
        """Return names of all ``.textfsm`` and ``.ttp`` templates reachable."""
        templates = []
        for path in self._roots:
            for file in Path(path).rglob("*"):
                if file.suffix in (".textfsm", ".ttp"):
                    templates.append(file.name)
        return templates
