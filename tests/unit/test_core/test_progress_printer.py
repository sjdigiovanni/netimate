# SPDX-License-Identifier: MPL-2.0
import time
from netimate.view.shell.progress_printer import ProgressPrinter


def test_progress_printer_start_stop(monkeypatch):
    printer = ProgressPrinter("Testing")
    printer.start()
    time.sleep(0.1)
    printer.stop()
