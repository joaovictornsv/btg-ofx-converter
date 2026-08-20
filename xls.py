"""Parse BTG Pactual bank statement XLS exports into transactions."""

from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from models import Transaction

try:
    import xlrd
except ImportError:  # pragma: no cover - exercised when xlrd is missing
    xlrd = None

_COL_DATE = 1
_COL_CATEGORY = 2
_COL_TYPE = 3
_COL_DESCRIPTION = 6
_COL_AMOUNT = 10

_PERIOD_RE = re.compile(
    r"(\d{2})/(\d{2})/(\d{4})\s+a\s+(\d{2})/(\d{2})/(\d{4})"
)
_DATETIME_RE = re.compile(r"^(\d{2})/(\d{2})/(\d{4})(?:\s+(\d{2}):(\d{2}))?$")


def parse_xls(path: Path | str) -> tuple[str, str, list[Transaction]]:
    """Return (period_start, period_end, transactions) from a BTG XLS export."""
    if xlrd is None:
        raise ImportError(
            "Reading .xls files requires xlrd. Install it with: pip install xlrd"
        )

    workbook = xlrd.open_workbook(str(path))
    sheet = workbook.sheet_by_index(0)
    period_start, period_end = _extract_period(sheet)
    transactions = _extract_transactions(sheet)
    return period_start, period_end, transactions


def _extract_period(sheet: xlrd.sheet.Sheet) -> tuple[str, str]:
    for row in range(sheet.nrows):
        label = _cell_str(sheet, row, 1)
        if label != "Período do extrato:":
            continue
        period_text = _cell_str(sheet, row, 2)
        match = _PERIOD_RE.search(period_text)
        if not match:
            break
        start_day, start_month, start_year, end_day, end_month, end_year = match.groups()
        return (
            f"{start_year}{start_month}{start_day}000000",
            f"{end_year}{end_month}{end_day}235959",
        )
    return "?", "?"


def _extract_transactions(sheet: xlrd.sheet.Sheet) -> list[Transaction]:
    transactions: list[Transaction] = []
    in_table = False

    for row in range(sheet.nrows):
        date_label = _cell_str(sheet, row, _COL_DATE)
        if date_label == "Data e hora":
            in_table = True
            continue
        if not in_table:
            continue

        if not _DATETIME_RE.match(date_label):
            continue

        description = _cell_str(sheet, row, _COL_DESCRIPTION)
        if description == "Saldo Diário":
            continue

        amount = _cell_decimal(sheet, row, _COL_AMOUNT)
        category = _cell_str(sheet, row, _COL_CATEGORY)
        trn_type = _cell_str(sheet, row, _COL_TYPE)
        memo = " ".join(part for part in (trn_type, category) if part)

        transactions.append(
            Transaction(
                trn_type=trn_type or "UNKNOWN",
                date=_to_ofx_datetime(date_label),
                amount=amount,
                memo=memo,
                name=description,
            )
        )

    return transactions


def _to_ofx_datetime(value: str) -> str:
    match = _DATETIME_RE.match(value)
    if not match:
        return value

    day, month, year, hour, minute = match.groups()
    hour = hour or "00"
    minute = minute or "00"
    return f"{year}{month}{day}{hour}{minute}00"


def _cell_str(sheet: xlrd.sheet.Sheet, row: int, col: int) -> str:
    if col >= sheet.ncols:
        return ""
    value = sheet.cell_value(row, col)
    if value == "":
        return ""
    if sheet.cell_type(row, col) == xlrd.XL_CELL_DATE:
        return _format_excel_date(value)
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def _format_excel_date(value: float) -> str:
    dt = datetime(*xlrd.xldate_as_tuple(value, 0)[:6])
    return dt.strftime("%d/%m/%Y %H:%M")


def _cell_decimal(sheet: xlrd.sheet.Sheet, row: int, col: int) -> Decimal:
    if col >= sheet.ncols:
        return Decimal("0")

    value = sheet.cell_value(row, col)
    if value == "":
        return Decimal("0")
    if isinstance(value, (int, float)):
        return Decimal(str(value)).quantize(Decimal("0.01"))
    normalized = str(value).strip().replace(".", "").replace(",", ".")
    return Decimal(normalized).quantize(Decimal("0.01"))
