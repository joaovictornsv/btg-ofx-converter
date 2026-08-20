"""Tests for BTG credit card fatura XLSX parsing."""

from __future__ import annotations

import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from fatura import parse_fatura

openpyxl = None
try:
    import openpyxl
except ImportError:
    pass


def build_sample_workbook(path: Path) -> None:
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet["B3"] = "Fatura Cartão de Crédito"
    sheet["G3"] = "Agosto/2026"
    sheet["B7"] = "Período de Compras"
    sheet["D7"] = "10/07 até 11/08"
    sheet["B8"] = "Vencimento"
    sheet["D8"] = "15/08"
    sheet["B20"] = "Data"
    sheet["C20"] = "Descrição"
    sheet["E20"] = "Valor"
    sheet["F20"] = "Tipo de compra"
    sheet["B21"] = date(2026, 7, 28)
    sheet["C21"] = "Cursor Ai Powered Ide"
    sheet["E21"] = 338.93
    sheet["F21"] = "Compra internacional"
    sheet["B22"] = date(2026, 8, 6)
    sheet["C22"] = "Pizzaria Paulistana"
    sheet["E22"] = 32.46
    sheet["F22"] = "Compra à vista"
    workbook.save(path)


@unittest.skipIf(openpyxl is None, "openpyxl is not installed")
class ParseFaturaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "2026-08-15_Fatura_BTG.xlsx"
        build_sample_workbook(self.path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_period_dates(self) -> None:
        start, end, _ = parse_fatura(self.path)
        self.assertEqual(start, "20260710000000")
        self.assertEqual(end, "20260811235959")

    def test_transactions_are_expenses_with_merchant_names(self) -> None:
        _, _, txns = parse_fatura(self.path)
        self.assertEqual(len(txns), 2)

        cursor = txns[0]
        self.assertEqual(cursor.name, "Cursor Ai Powered Ide")
        self.assertEqual(cursor.amount, Decimal("-338.93"))
        self.assertEqual(cursor.date, "20260728000000")

        pizza = txns[1]
        self.assertEqual(pizza.name, "Pizzaria Paulistana")
        self.assertEqual(pizza.amount, Decimal("-32.46"))
        self.assertEqual(pizza.memo, "Compra à vista")


if __name__ == "__main__":
    unittest.main()
