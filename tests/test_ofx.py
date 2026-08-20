"""Tests for OFX parsing and writing."""

from __future__ import annotations

import unittest
from decimal import Decimal

from models import Transaction
from ofx import parse_ofx, write_ofx


SAMPLE_OFX = """\
garbage preamble
<OFX>
<BANKMSGSRSV1>
<STMTTRNRS>
<STMTRS>
<BANKTRANLIST>
<DTSTART>20260101000000</DTSTART>
<DTEND>20260131235959</DTEND>
<STMTTRN>
<TRNTYPE>DEBIT</TRNTYPE>
<DTPOSTED>20260115120000</DTPOSTED>
<TRNAMT>-42.50</TRNAMT>
<MEMO>Uber trip</MEMO>
<NAME>UBER</NAME>
</STMTTRN>
<STMTTRN>
<TRNTYPE>CREDIT</TRNTYPE>
<DTPOSTED>20260120120000</DTPOSTED>
<TRNAMT>5000.00</TRNAMT>
<MEMO>Salary</MEMO>
<NAME>ACME LTDA</NAME>
</STMTTRN>
</BANKTRANLIST>
</STMTRS>
</STMTTRNRS>
</BANKMSGSRSV1>
</OFX>
"""


class ParseOfxTests(unittest.TestCase):
    def test_period_dates(self) -> None:
        start, end, _ = parse_ofx(SAMPLE_OFX)
        self.assertEqual(start, "20260101000000")
        self.assertEqual(end, "20260131235959")

    def test_transactions(self) -> None:
        _, _, txns = parse_ofx(SAMPLE_OFX)
        self.assertEqual(len(txns), 2)

        expense = txns[0]
        self.assertEqual(expense.trn_type, "DEBIT")
        self.assertEqual(expense.date, "20260115120000")
        self.assertEqual(expense.amount, Decimal("-42.50"))
        self.assertEqual(expense.memo, "Uber trip")
        self.assertEqual(expense.name, "UBER")

        income = txns[1]
        self.assertEqual(income.amount, Decimal("5000.00"))

    def test_strips_preamble_before_ofx_tag(self) -> None:
        _, _, txns = parse_ofx("junk\n" + SAMPLE_OFX)
        self.assertEqual(len(txns), 2)

    def test_missing_tags_default_to_empty_or_zero(self) -> None:
        minimal = """<OFX><STMTTRN></STMTTRN></OFX>"""
        start, end, txns = parse_ofx(minimal)
        self.assertEqual(start, "?")
        self.assertEqual(end, "?")
        self.assertEqual(len(txns), 1)
        self.assertEqual(txns[0].amount, Decimal("0"))


class WriteOfxTests(unittest.TestCase):
    def test_writes_required_structure(self) -> None:
        content = write_ofx(
            "20260101000000",
            "20260131235959",
            [
                Transaction(
                    trn_type="DEBIT",
                    date="20260115120000",
                    amount=Decimal("-42.50"),
                    memo="Uber trip",
                    name="UBER",
                )
            ],
        )
        self.assertIn("OFXHEADER:100", content)
        self.assertIn("<DTSTART>20260101000000</DTSTART>", content)
        self.assertIn("<DTEND>20260131235959</DTEND>", content)
        self.assertIn("<ACCTTYPE>CHECKING</ACCTTYPE>", content)
        self.assertIn("<TRNTYPE>DEBIT</TRNTYPE>", content)
        self.assertIn("<TRNAMT>-42.50</TRNAMT>", content)
        self.assertIn("<MEMO>Uber trip</MEMO>", content)
        self.assertIn("<NAME>UBER</NAME>", content)
        self.assertRegex(content, r"<FITID>[0-9a-f]{16}</FITID>")

    def test_write_ofx_credit_card_acct_type(self) -> None:
        content = write_ofx(
            "20260710000000",
            "20260811235959",
            [],
            acct_type="CREDITCARD",
        )
        self.assertIn("<ACCTTYPE>CREDITCARD</ACCTTYPE>", content)
        self.assertNotIn("<ACCTTYPE>CHECKING</ACCTTYPE>", content)

    def test_escapes_special_characters(self) -> None:
        content = write_ofx(
            "20260101000000",
            "20260131235959",
            [
                Transaction(
                    trn_type="DEBIT",
                    date="20260115120000",
                    amount=Decimal("-1.00"),
                    memo="A & B <test>",
                    name="Shop > Store",
                )
            ],
        )
        self.assertIn("<MEMO>A &amp; B &lt;test&gt;</MEMO>", content)
        self.assertIn("<NAME>Shop &gt; Store</NAME>", content)

    def test_fitids_are_stable(self) -> None:
        transaction = Transaction(
            trn_type="DEBIT",
            date="20260115120000",
            amount=Decimal("-1.00"),
            memo="memo",
            name="name",
        )
        first = write_ofx("20260101000000", "20260131235959", [transaction])
        second = write_ofx("20260101000000", "20260131235959", [transaction])
        self.assertEqual(first, second)

    def test_round_trip_preserves_transactions(self) -> None:
        original = [
            Transaction(
                trn_type="DEBIT",
                date="20260115120000",
                amount=Decimal("-42.50"),
                memo="Uber trip",
                name="UBER",
            ),
            Transaction(
                trn_type="CREDIT",
                date="20260120120000",
                amount=Decimal("5000.00"),
                memo="Salary",
                name="ACME LTDA",
            ),
        ]
        content = write_ofx("20260101000000", "20260131235959", original)
        start, end, parsed = parse_ofx(content)
        self.assertEqual(start, "20260101000000")
        self.assertEqual(end, "20260131235959")
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0].trn_type, original[0].trn_type)
        self.assertEqual(parsed[0].date, original[0].date)
        self.assertEqual(parsed[0].amount, original[0].amount)
        self.assertEqual(parsed[0].memo, original[0].memo)
        self.assertEqual(parsed[0].name, original[0].name)

    def test_round_trip_unescapes_special_characters(self) -> None:
        original = Transaction(
            trn_type="DEBIT",
            date="20260115120000",
            amount=Decimal("-1.00"),
            memo="A & B <test>",
            name="Shop > Store",
        )
        _, _, parsed = parse_ofx(
            write_ofx("20260101000000", "20260131235959", [original])
        )
        self.assertEqual(parsed[0].memo, original.memo)
        self.assertEqual(parsed[0].name, original.name)


if __name__ == "__main__":
    unittest.main()
