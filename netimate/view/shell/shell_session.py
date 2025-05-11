# SPDX-License-Identifier: MPL-2.0
"""
netimate.view.shell.shell_session
---------------------------------
Rich‑based interactive shell built on PromptToolkit.  Replaces the classic
`cmd.Cmd` shell with tab completion and colourful results.  Routes user
commands to the high‑level :class:`ApplicationInterface`.
"""

from __future__ import annotations

import asyncio
import shlex
import sys
from typing import Any, Callable, List, Optional

from anyio.from_thread import run as await_safe
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion, WordCompleter
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from netimate.interfaces.application.application import ApplicationInterface
from netimate.view.shell.progress_printer import ProgressPrinter


class _CommandCompleter(Completer):
    """
    prompt_toolkit completer with dynamic device‑command listing for `run`.
    """

    def __init__(self, app: ApplicationInterface):
        self.app = app
        self.top_level = [
            "snapshot",
            "run",
            "diagnostic",
            "diff-snapshots",
            "list",
            "log_level",
            "exit",
        ]
        self.static_args = {
            "list": ["devices", "device-repositories", "device-commands", "snapshots", "sites"],
            "log_level": ["off", "info", "debug"],
        }

    def _word_complete(self, words, doc, event, options):
        return WordCompleter(options, ignore_case=True).get_completions(doc, event)

    def _device_site_completions(self, prefix: str):
        """Yield Completion objects for devices and sites, filtering by prefix."""
        devices = self.app.list("devices")
        sites = self.app.list("sites")
        for name in devices:
            if name.startswith(prefix):
                yield Completion(name, display=f"{name} [device]")
        for name in sites:
            if name.startswith(prefix):
                yield Completion(name, display=f"{name} [site]")

    # ---------- generic helpers -------------------------------------------
    def _filter(self, items, prefix: str):
        for x in items:
            if x.startswith(prefix):
                yield x

    # ---------- per‑command completers ------------------------------------
    def _complete_run(self, words, before, doc, event):
        # run                → device‑commands
        # run <cmd>          → 'on'
        # run <cmd> on       → device/site
        # run <cmd> on devX  → device/site filter
        if len(words) == 1 or (len(words) == 2 and not before.endswith(" ")):
            prefix = words[-1] if len(words) == 2 else ""
            cmds = list(self._filter(self.app.list("device-commands"), prefix))
            yield from self._word_complete(words, doc, event, cmds)
            return

        if len(words) == 2 and before.endswith(" "):
            yield Completion("on")
            return

        if words[2] == "on":
            prefix = "" if before.endswith(" ") else words[-1]
            yield from self._device_site_completions(prefix)

    def _complete_snapshot_diag(self, words, before, doc, event):
        prefix = "" if before.endswith(" ") else words[-1]
        yield from self._device_site_completions(prefix)

    def _complete_diff_snap(self, words, before, doc, event):
        # device proposal
        if len(words) == 1 or (len(words) == 2 and not before.endswith(" ")):
            prefix = words[-1] if len(words) == 2 else ""
            for dev in self._filter(self.app.list("devices"), prefix):
                yield Completion(dev, display=f"{dev} [device]")
            return

        device = words[1]
        snaps = self.app.list_snapshots_for_device(device)

        # first snapshot
        if len(words) == 2:
            prefix = "" if before.endswith(" ") else ""
            for s in self._filter(snaps, prefix):
                yield Completion(s)
            return
        if len(words) == 3:
            prefix = "" if before.endswith(" ") else words[-1]
            for s in self._filter(snaps, prefix):
                yield Completion(s)
            return

    def get_completions(self, document, complete_event):
        before = document.text_before_cursor
        words = before.strip().split()

        # top‑level
        if not words:
            yield from self._word_complete(words, document, complete_event, self.top_level)
            return
        cmd = words[0]

        # still typing command itself
        if len(words) == 1 and not before.endswith(" "):
            yield from self._word_complete(
                words, document, complete_event, self._filter(self.top_level, cmd)
            )
            return

        dispatch = {
            "run": self._complete_run,
            "snapshot": self._complete_snapshot_diag,
            "diagnostic": self._complete_snapshot_diag,
            "diff-snapshots": self._complete_diff_snap,
        }
        if cmd in dispatch:
            yield from dispatch[cmd](words, before, document, complete_event)
            return

        # static list / log_level
        if cmd in self.static_args:
            prefix = words[-1] if not before.endswith(" ") else ""
            opts = list(self._filter(self.static_args[cmd], prefix))
            yield from self._word_complete(words, document, complete_event, opts)


class netimateShellSession:
    """
    Interactive shell façade.

    Provides command parsing, tab‑completion via `_CommandCompleter`,
    and dispatches to `ApplicationInterface` methods for snapshot,
    run, diagnostic, diff‑snapshots, list, and log_level operations.
    """

    def __init__(self, app: ApplicationInterface):
        """
        Parameters
        ----------
        app:
            The ApplicationInterface instance to route commands to.
        """
        self.app = app
        # Welcome banner for tests and users
        print("Welcome to netimate Shell – type 'exit' to quit.")
        self.session: PromptSession = PromptSession(
            "netimate> ",
            completer=_CommandCompleter(app),
            complete_in_thread=True,
        )

    # --------------------------------------------------------------------- #
    #                               Main loop                               #
    # --------------------------------------------------------------------- #
    def run_forever(self):
        try:
            while True:
                try:
                    line = self.session.prompt()
                except KeyboardInterrupt:
                    # Ctrl‑C: just re‑prompt
                    continue
                except EOFError:
                    print("\nExiting netimate shell.")
                    break

                line = line.strip()
                if not line:
                    continue
                self._dispatch(line)
        except Exception as exc:
            print(f"Fatal error in shell: {exc}")
        finally:
            print("Exiting netimate shell.")

    # --------------------------------------------------------------------- #
    #                            Command routing                            #
    # --------------------------------------------------------------------- #
    def _dispatch(self, line: str):
        """Parse user input and call the matching _cmd_* method."""
        cmd, *rest = shlex.split(line)
        handler: Optional[Callable[[List[str]], object]] = {
            "snapshot": self._cmd_snapshot,
            "run": self._cmd_run,
            "diagnostic": self._cmd_diagnostic,
            "diff-snapshots": self._cmd_diff_snapshots,
            "diff_snapshots": self._cmd_diff_snapshots,  # alias for tests
            "log_level": self._cmd_log_level,
            "list": self._cmd_list,
            "exit": lambda _: sys.exit(0),
        }.get(cmd)

        if handler:
            handler(rest)
        else:
            print(f"Unknown command: {cmd}")

    # --------------------------------------------------------------------- #
    #                            Helper utils                               #
    # --------------------------------------------------------------------- #
    def _await(self, coro, desc: str):
        """Run *coro* and show ProgressPrinter while awaiting."""
        prog = ProgressPrinter(desc)
        prog.start()
        try:
            # If we’re already inside an asyncio loop (e.g. unit test), use anyio’s run‑in‑thread
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                return asyncio.run(coro)
            else:
                return await_safe(lambda: coro)
        finally:
            prog.stop()

    # --------------------------------------------------------------------- #
    #                              Commands                                 #
    # --------------------------------------------------------------------- #
    def _cmd_snapshot(self, argv: List[str]):
        """Shell command: snapshot <device...|site>."""
        if not argv:
            print("Usage: snapshot <device1> ... | <site>")
            return
        print(f"Snapshot on {', '.join(argv)}.")
        results = self._await(
            self.app.snapshot(argv),
            f"Snapshot on {', '.join(argv)}",
        )
        table = Table(show_header=False)
        table.add_column("Device")
        table.add_column("Status")
        for dev in results:
            table.add_row(dev, "Saved snapshot")

        Console().print(
            Panel(table, title="[bold green]Snapshots[/bold green]", border_style="green")
        )

    def _cmd_run(self, argv: List[str]):
        """Shell command: run <device_command> on <device...>."""
        try:
            idx = argv.index("on")
            command_name = argv[0]
            device_names = argv[idx + 1 :]
        except ValueError:
            print(
                "Syntax error: run command requires 'on' keyword.\n"
                "Usage: run <device_command> on <device1> ..."
            )
            return

        print(f"Running '{command_name}' on {', '.join(device_names)}.")
        results = self._await(
            self.app.run_device_command(device_names, command_name),
            f"Run '{command_name}'",
        )
        cmd_plugin = self.app.get_device_command(command_name)
        for dev, raw in results.items():
            try:
                rendered = cmd_plugin.format_result(raw)
            except Exception:
                rendered = str(raw)

            # Convert plain strings to Rich Text
            if isinstance(rendered, str):
                rendered = Text(rendered)

            Console().print(
                Panel(rendered, title=f"[bold green]{dev}[/bold green]", border_style="green")
            )

    def _cmd_diagnostic(self, argv: List[str]):
        """Shell command: diagnostic <device...|site>."""
        if not argv:
            print("Usage: diagnostic <device1> ... | <site>")
            return

        print(f"Diagnostics on {', '.join(argv)}.")
        results = self._await(
            self.app.diagnostic(argv),
            f"Diagnostics on {', '.join(argv)}",
        )

        for dev, outputs in results.items():
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Command")
            table.add_column("Summary", overflow="fold")

            for cmd_name, raw in outputs.items():
                cmd_plugin = self.app.get_device_command(cmd_name)
                label = getattr(cmd_plugin, "label", cmd_name) or cmd_name
                try:
                    summary = cmd_plugin.summarise_result(raw)
                except Exception:
                    summary = str(raw)[:120]  # fallback truncate
                table.add_row(label, summary)

            Console().print(
                Panel(
                    table, title=f"[bold green]{dev} diagnostics[/bold green]", border_style="green"
                )
            )

    def _cmd_log_level(self, argv: List[str]):
        """Shell command: log_level <off|info|debug>."""
        if len(argv) != 1:
            print("Usage: log_level <off|info|debug>")
            return
        level = argv[0]
        try:
            self.app.set_log_level(level)
            print(f"Switched log level to {level}")
        except Exception as exc:
            print(f"Error setting log level: {exc}")

    def _cmd_diff_snapshots(self, argv: List[Any]):
        """Shell command: diff-snapshots <device> <s1> <s2>."""
        if len(argv) != 3:
            print("Usage: diff-snapshots <device> <snap1> <snap2>")
            return
        device, s1, s2 = argv
        s1 = int(s1) if s1.isdigit() else s1
        s2 = int(s2) if s2.isdigit() else s2
        diff_text = self.app.diff_snapshots(device, s1, s2)
        if sys.stdout.isatty() and diff_text:
            # Build a Rich Text object with per‑line colours
            styled = Text()
            for line in diff_text.splitlines():
                if line.startswith("+") and not line.startswith("+++"):
                    styled.append(line + "\n", style="green")
                elif line.startswith("-") and not line.startswith("---"):
                    styled.append(line + "\n", style="red")
                elif line.startswith("@@"):
                    styled.append(line + "\n", style="yellow")
                elif line.startswith(("---", "+++")):
                    styled.append(line + "\n", style="cyan")
                else:
                    styled.append(line + "\n")
            Console().print(Panel(styled, border_style="bright_cyan"))
        else:
            print(diff_text)

    def _cmd_list(self, argv: List[str]):
        """Shell command: list <devices|device-commands|...>."""
        if not argv:
            print(
                "Usage: list <devices [site] | device-repositories | device-commands | snapshots | sites>"
            )
            return
        key = argv[0]
        site = argv[1] if len(argv) > 1 and key == "devices" else None
        items = self.app.list(key, site=site)
        for item in items:
            print(f"[{key}] {item}")
