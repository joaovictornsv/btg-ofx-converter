#!/usr/bin/env python3
"""Generate synthetic BTG export fixtures for examples/ and CI smoke tests."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
sys.path.insert(0, str(ROOT))

from tests.test_fatura import build_sample_workbook
from tests.test_xls import SAMPLE_ROWS


def write_sample_extrato(path: Path) -> None:
    import xlwt

    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("Extrato")

    for row_index, row in enumerate(SAMPLE_ROWS):
        for col_index, value in enumerate(row):
            if value == "":
                continue
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                sheet.write(row_index, col_index, float(value))
            else:
                sheet.write(row_index, col_index, str(value))

    workbook.save(str(path))


def main() -> int:
    EXAMPLES.mkdir(parents=True, exist_ok=True)

    extrato_path = EXAMPLES / "sample_extrato.xls"
    fatura_path = EXAMPLES / "sample_fatura.xlsx"

    write_sample_extrato(extrato_path)
    build_sample_workbook(fatura_path)

    print(f"Wrote {extrato_path}")
    print(f"Wrote {fatura_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
