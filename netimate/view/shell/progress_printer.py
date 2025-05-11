# SPDX-License-Identifier: MPL-2.0
"""
netimate.view.shell.progress_printer
------------------------------------
Tiny utility that shows a "Working..." progress indicator (dots)
in the console while an awaitable operation runs in the background.
Used by `shell_session.py` to give feedback during long‑running tasks.
"""

import sys
import threading
import time


class ProgressPrinter:
    """
    Simple console spinner that appends one dot every 0.5 s.

    Usage
    -----
    >>> prog = ProgressPrinter("Snapshot on r1")
    >>> prog.start()
    >>> long_running_fn()
    >>> prog.stop()
    """

    def __init__(self, message="Working"):
        """
        Parameters
        ----------
        message:
            Introductory text written once before the dots.
        """
        self.message = message
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        sys.stdout.write(self.message)
        sys.stdout.flush()
        while not self._stop.is_set():
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(0.5)
        sys.stdout.write("\n")
        sys.stdout.flush()

    def start(self):
        """Start background thread that prints dots."""
        self._thread.start()

    def stop(self):
        """Signal thread to stop and wait for termination."""
        self._stop.set()
        self._thread.join()
