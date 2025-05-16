# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from netimate.application.command_executor_service import CommandExecutorService


class SnapshotService:
    def __init__(
        self,
        executor: CommandExecutorService,
        snapshot_dir: Path = Path("snapshots")
    ):
        self._executor = executor
        self._snapshot_dir = snapshot_dir

    async def snapshot(self, device_names: List[str]) -> Dict[str, str]:
        results = await self._executor.run(device_names, "show-running-config")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._snapshot_dir.mkdir(parents=True, exist_ok=True)

        for device, output in results.items():
            file_path = self._snapshot_dir / f"{device}_running_config_{timestamp}.txt"
            if isinstance(output, dict) and "config_lines" in output:
                file_path.write_text("\n".join(output["config_lines"]))
            else:
                file_path.write_text(str(output))

        return results
