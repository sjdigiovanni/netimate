# SPDX-License-Identifier: MPL-2.0
import asyncio

from netimate.interfaces.application.application import ApplicationInterface


def run_cli_mode(app: ApplicationInterface, args, parser):
    """
    One‑shot CLI execution. Returns the JSON‑serializable result.
    """
    # validate required parameters
    for param in ("device_names", "command"):
        if getattr(args, param) is None:
            parser.error(f"--{param.replace('_', '-')} is required in CLI mode.")

    results = asyncio.run(
        app.run_device_command(device_names=args.device_names, command_name=args.command)
    )

    for device, result in results.items():
        print("---")
        print(f"[{device}]")
        try:
            command = app.get_device_command(args.command)
            formatted_result = command.format_result(result)
        except Exception:
            formatted_result = str(result)
        print(formatted_result)

    return results
