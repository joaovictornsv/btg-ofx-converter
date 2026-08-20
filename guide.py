"""Copy the bundled usage guide beside user output files."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

GUIDE_FILENAME = "guia-btg-ofx.md"


def guide_source_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "docs" / GUIDE_FILENAME
    return Path(__file__).resolve().parent / "docs" / GUIDE_FILENAME


def write_guide_copy(output_dir: Path) -> None:
    source = guide_source_path()
    if not source.exists():
        return
    destination = output_dir / GUIDE_FILENAME
    if destination.exists():
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
