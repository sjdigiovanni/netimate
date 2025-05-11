# SPDX-License-Identifier: MPL-2.0
from typing import List, Tuple


def parse_run_syntax(arg: str) -> Tuple[str, List[str]]:
    """
    Parses shell input like:
    run show-version on R1,R2

    Returns:
        (command_name, device_names (list), runner_name (or None))
    """
    if " on " not in arg:
        raise ValueError("Expected syntax: run <command> on <device>[,<device>] [using --runner=x]")

    command_part, devices_part = arg.split(" on ", 1)
    command_name = command_part.strip()
    device_names = [d.strip() for d in devices_part.split(",") if d.strip()]

    return command_name, device_names
