# SPDX-License-Identifier: MPL-2.0
import pytest

from netimate.application.snapshot_service import SnapshotService


@pytest.mark.asyncio
async def test_snapshot_saves_output(tmp_path, mock_runner):
    class DummyCommand:
        pass

    mock_runner.run.return_value = {"r1": {"config_lines": ["line1", "line2"]}}
    snapshot_dir = tmp_path / "snapshots"
    snapshot_service = SnapshotService(mock_runner, snapshot_dir=snapshot_dir)

    result = await snapshot_service.snapshot(["r1"])
    assert "r1" in result
    files = list(snapshot_dir.glob("r1_running_config_*.txt"))
    assert files
    assert files[0].read_text() == "line1\nline2"
