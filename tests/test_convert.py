"""Tests for the BTG OFX conversion CLI."""

from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import convert
from models import Transaction
from tests.test_xls import FakeSheet, SAMPLE_ROWS

xlrd = None
try:
    import xlrd
except ImportError:
    pass

openpyxl = None
try:
    import openpyxl
except ImportError:
    pass


class ConvertCheckingTests(unittest.TestCase):
    @patch("convert.parse_xls")
    def test_writes_sibling_ofx_file(self, mock_parse_xls: MagicMock) -> None:
        mock_parse_xls.return_value = (
            "20260101000000",
            "20260131235959",
            [
                Transaction(
                    trn_type="DEBIT",
                    date="20260115120000",
                    amount=Decimal("-10.00"),
                    memo="memo",
                    name="Store",
                )
            ],
        )
        input_path = Path("extrato.xls")
        output_path = Path("extrato.ofx")
        input_path.touch()
        output_path.unlink(missing_ok=True)

        try:
            with patch.object(sys, "argv", ["convert.py", "checking", str(input_path)]):
                exit_code = convert.main()
            self.assertEqual(exit_code, 0)
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("<OFX>", content)
            self.assertIn("<ACCTTYPE>CHECKING</ACCTTYPE>", content)
            self.assertIn("<NAME>Store</NAME>", content)
        finally:
            input_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)

    def test_missing_file_returns_error(self) -> None:
        with patch.object(sys, "argv", ["convert.py", "checking", "missing.xls"]):
            exit_code = convert.main()
        self.assertEqual(exit_code, 1)

    def test_unsupported_extension_returns_error(self) -> None:
        csv_path = Path("statement.csv")
        csv_path.touch()
        try:
            with patch.object(sys, "argv", ["convert.py", "checking", str(csv_path)]):
                exit_code = convert.main()
            self.assertEqual(exit_code, 1)
        finally:
            csv_path.unlink(missing_ok=True)

    @unittest.skipIf(xlrd is None, "xlrd is not installed")
    @patch("xls.xlrd.open_workbook")
    def test_integration_with_mocked_workbook(self, mock_open_workbook: MagicMock) -> None:
        mock_open_workbook.return_value.sheet_by_index.return_value = FakeSheet(SAMPLE_ROWS)
        input_path = Path("cli-extrato.xls")
        output_path = Path("cli-extrato.ofx")
        input_path.touch()
        output_path.unlink(missing_ok=True)

        try:
            with patch.object(sys, "argv", ["convert.py", "checking", str(input_path)]):
                exit_code = convert.main()
            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())
            self.assertIn(
                "<DTSTART>20260101000000</DTSTART>",
                output_path.read_text(encoding="utf-8"),
            )
        finally:
            input_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)


@unittest.skipIf(openpyxl is None, "openpyxl is not installed")
class ConvertCardTests(unittest.TestCase):
    @patch("convert.parse_fatura")
    def test_writes_sibling_ofx_with_credit_card_type(
        self, mock_parse_fatura: MagicMock
    ) -> None:
        mock_parse_fatura.return_value = (
            "20260710000000",
            "20260811235959",
            [
                Transaction(
                    trn_type="Compra à vista",
                    date="20260806000000",
                    amount=Decimal("-32.46"),
                    memo="Compra à vista",
                    name="Pizzaria Paulistana",
                )
            ],
        )
        input_path = Path("fatura.xlsx")
        output_path = Path("fatura.ofx")
        input_path.touch()
        output_path.unlink(missing_ok=True)

        try:
            with patch.object(sys, "argv", ["convert.py", "card", str(input_path)]):
                exit_code = convert.main()
            self.assertEqual(exit_code, 0)
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("<ACCTTYPE>CREDITCARD</ACCTTYPE>", content)
            self.assertIn("<NAME>Pizzaria Paulistana</NAME>", content)
        finally:
            input_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)

    def test_missing_file_returns_error(self) -> None:
        with patch.object(sys, "argv", ["convert.py", "card", "missing.xlsx"]):
            exit_code = convert.main()
        self.assertEqual(exit_code, 1)

    def test_unsupported_extension_returns_error(self) -> None:
        xls_path = Path("fatura.xls")
        xls_path.touch()
        try:
            with patch.object(sys, "argv", ["convert.py", "card", str(xls_path)]):
                exit_code = convert.main()
            self.assertEqual(exit_code, 1)
        finally:
            xls_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
