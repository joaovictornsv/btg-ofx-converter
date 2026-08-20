"""Tests for BTG XLS parsing."""

from __future__ import annotations

import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

from ofx import parse_ofx, write_ofx
from xls import parse_xls

xlrd = None
try:
    import xlrd
except ImportError:
    pass


class FakeSheet:
    def __init__(self, rows: list[list[object]]) -> None:
        self._rows = rows
        self.nrows = len(rows)
        self.ncols = max((len(row) for row in rows), default=0)

    def cell_value(self, row: int, col: int) -> object:
        if row >= self.nrows or col >= len(self._rows[row]):
            return ""
        return self._rows[row][col]

    def cell_type(self, row: int, col: int) -> int:
        value = self.cell_value(row, col)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return 2
        return 1


SAMPLE_ROWS = [
    ["", "Extrato de conta corrente"],
    [],
    ["", "Período do extrato:", "01/01/2026 a 31/01/2026"],
    [],
    ["", "Data e hora", "Categoria", "Transação", "", "", "Descrição", "", "", "", "Valor"],
    ["", "15/01/2026 12:00", "Alimentação", "Compra no débito autorizada", "", "", "Grocery Store", "", "", "", -42.50],
    ["", "15/01/2026 23:59", "", "", "", "", "Saldo Diário", "", "", "", 57.50],
    ["", "20/01/2026 12:00", "Transferência", "Pix recebido", "", "", "ACME LTDA", "", "", "", 5000.00],
    [],
    ["", "Extrato de conta corrente"],
    [],
    ["", "Período do extrato:", "01/01/2026 a 31/01/2026"],
    [],
    ["", "Data e hora", "Categoria", "Transação", "", "", "Descrição", "", "", "", "Valor"],
    ["", "25/01/2026 18:30", "Transporte", "Compra no débito autorizada", "", "", "Uber", "", "", "", -10.00],
]


@unittest.skipIf(xlrd is None, "xlrd is not installed")
class ParseXlsTests(unittest.TestCase):
    @patch("xls.xlrd.open_workbook")
    def test_period_dates(self, mock_open_workbook: MagicMock) -> None:
        mock_open_workbook.return_value.sheet_by_index.return_value = FakeSheet(SAMPLE_ROWS)
        start, end, _ = parse_xls(Path("extrato.xls"))
        self.assertEqual(start, "20260101000000")
        self.assertEqual(end, "20260131235959")

    @patch("xls.xlrd.open_workbook")
    def test_transactions_skip_daily_balance_and_merge_pages(
        self, mock_open_workbook: MagicMock
    ) -> None:
        mock_open_workbook.return_value.sheet_by_index.return_value = FakeSheet(SAMPLE_ROWS)
        _, _, txns = parse_xls(Path("extrato.xls"))
        self.assertEqual(len(txns), 3)

        expense = txns[0]
        self.assertEqual(expense.trn_type, "Compra no débito autorizada")
        self.assertEqual(expense.date, "20260115120000")
        self.assertEqual(expense.amount, Decimal("-42.50"))
        self.assertEqual(expense.memo, "Compra no débito autorizada Alimentação")
        self.assertEqual(expense.name, "Grocery Store")

        income = txns[1]
        self.assertEqual(income.amount, Decimal("5000.00"))
        self.assertEqual(income.name, "ACME LTDA")

        second_page = txns[2]
        self.assertEqual(second_page.name, "Uber")
        self.assertEqual(second_page.amount, Decimal("-10.00"))


@unittest.skipIf(xlrd is None, "xlrd is not installed")
class XlsToOfxRoundTripTests(unittest.TestCase):
    @patch("xls.xlrd.open_workbook")
    def test_xls_round_trip_matches_original_transactions(
        self, mock_open_workbook: MagicMock
    ) -> None:
        mock_open_workbook.return_value.sheet_by_index.return_value = FakeSheet(SAMPLE_ROWS)
        xls_start, xls_end, xls_txns = parse_xls(Path("extrato.xls"))
        ofx_start, ofx_end, ofx_txns = parse_ofx(
            write_ofx(xls_start, xls_end, xls_txns)
        )
        self.assertEqual(ofx_start, xls_start)
        self.assertEqual(ofx_end, xls_end)
        self.assertEqual(len(ofx_txns), len(xls_txns))
        for parsed, original in zip(ofx_txns, xls_txns):
            self.assertEqual(parsed.trn_type, original.trn_type)
            self.assertEqual(parsed.date, original.date)
            self.assertEqual(parsed.amount, original.amount)
            self.assertEqual(parsed.memo, original.memo)
            self.assertEqual(parsed.name, original.name)


if __name__ == "__main__":
    unittest.main()
