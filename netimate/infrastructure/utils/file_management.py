# SPDX-License-Identifier: MPL-2.0
from pathlib import Path


def find_file_upward(filename: str) -> Path:
    current_dir = Path.cwd()
    for parent in [current_dir] + list(current_dir.parents):
        candidate = parent / filename
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"Could not find '{filename}' in any parent directory from {current_dir}"
    )
