# SPDX-License-Identifier: MPL-2.0
"""
netimate.__main__
-----------------
CLI entry‑point installed by ``pip install netimate``.  Parses command‑line
options, wires the object graph via :func:`netimate.composition.composition_root`,
and then launches either the interactive Rich shell or a one‑shot CLI run.
"""
import argparse

from netimate.composition import composition_root
from netimate.view.cli.cli import run_cli_mode
from netimate.view.shell.shell_session import netimateShellSession


def main():
    """Entry‑point triggered by ``python ‑m netimate`` or ``netimate`` console script.

    Parses ``--device-names`` and ``--command`` for non‑interactive mode,
    or ``--shell`` to force interactive mode, then composes dependencies
    and dispatches to the chosen view.
    """
    # 1. Parse args
    parser = argparse.ArgumentParser(description="netimate: lightweight network automation tool")
    parser.add_argument("--device-names", nargs="+", help="one or more device names to target")
    parser.add_argument("--command", help="command plugin name")
    parser.add_argument("--shell", action="store_true", help="launch interactive shell")
    args = parser.parse_args()

    # 2. Compose object graph
    app = composition_root()

    # 3. Run view
    if args.shell or len(args.__dict__) == 0:
        netimateShellSession(app).run_forever()
    else:
        run_cli_mode(app, args, parser)


if __name__ == "__main__":
    main()
