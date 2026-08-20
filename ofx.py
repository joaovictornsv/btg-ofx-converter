"""Parse and write bank OFX statement files."""

from __future__ import annotations

import hashlib
import re
from decimal import Decimal

from models import Transaction


def parse_ofx(content: str) -> tuple[str, str, list[Transaction]]:
    """Return (period_start, period_end, transactions) from OFX content."""
    if "<OFX>" in content:
        content = content[content.index("<OFX>") :]

    period_start = _extract_tag(content, "DTSTART") or "?"
    period_end = _extract_tag(content, "DTEND") or "?"

    transactions: list[Transaction] = []
    for block in re.findall(r"<STMTTRN>(.*?)</STMTTRN>", content, re.DOTALL):
        amount_raw = _extract_tag(block, "TRNAMT")
        transactions.append(
            Transaction(
                trn_type=_extract_tag(block, "TRNTYPE"),
                date=_extract_tag(block, "DTPOSTED"),
                amount=Decimal(amount_raw or "0"),
                memo=_extract_tag(block, "MEMO"),
                name=_extract_tag(block, "NAME"),
            )
        )

    return period_start, period_end, transactions


def write_ofx(
    period_start: str,
    period_end: str,
    transactions: list[Transaction],
    acct_type: str = "CHECKING",
) -> str:
    """Serialize transactions into an OFX 1.x bank statement document."""
    lines = [
        "OFXHEADER:100",
        "DATA:OFXSGML",
        "VERSION:102",
        "SECURITY:NONE",
        "ENCODING:UTF-8",
        "CHARSET:1252",
        "COMPRESSION:NONE",
        "OLDFILEUID:NONE",
        "NEWFILEUID:NONE",
        "",
        "<OFX>",
        "<SIGNONMSGSRSV1>",
        "<SONRS>",
        "<STATUS>",
        "<CODE>0</CODE>",
        "<SEVERITY>INFO</SEVERITY>",
        "</STATUS>",
        f"<DTSERVER>{period_end}</DTSERVER>",
        "<LANGUAGE>POR</LANGUAGE>",
        "</SONRS>",
        "</SIGNONMSGSRSV1>",
        "<BANKMSGSRSV1>",
        "<STMTTRNRS>",
        "<TRNUID>0</TRNUID>",
        "<STATUS>",
        "<CODE>0</CODE>",
        "<SEVERITY>INFO</SEVERITY>",
        "</STATUS>",
        "<STMTRS>",
        "<CURDEF>BRL</CURDEF>",
        "<BANKACCTFROM>",
        "<BANKID>000</BANKID>",
        "<ACCTID>000000</ACCTID>",
        f"<ACCTTYPE>{acct_type}</ACCTTYPE>",
        "</BANKACCTFROM>",
        "<BANKTRANLIST>",
        f"<DTSTART>{period_start}</DTSTART>",
        f"<DTEND>{period_end}</DTEND>",
    ]

    for index, transaction in enumerate(transactions):
        lines.extend(
            [
                "<STMTTRN>",
                f"<TRNTYPE>{_escape_ofx_text(transaction.trn_type)}</TRNTYPE>",
                f"<DTPOSTED>{transaction.date}</DTPOSTED>",
                f"<TRNAMT>{_format_amount(transaction.amount)}</TRNAMT>",
                f"<FITID>{_fitid(transaction, index)}</FITID>",
                f"<MEMO>{_escape_ofx_text(transaction.memo)}</MEMO>",
                f"<NAME>{_escape_ofx_text(transaction.name)}</NAME>",
                "</STMTTRN>",
            ]
        )

    lines.extend(
        [
            "</BANKTRANLIST>",
            "<LEDGERBAL>",
            "<BALAMT>0.00</BALAMT>",
            f"<DTASOF>{period_end}</DTASOF>",
            "</LEDGERBAL>",
            "</STMTRS>",
            "</STMTTRNRS>",
            "</BANKMSGSRSV1>",
            "</OFX>",
        ]
    )
    return "\n".join(lines) + "\n"


def _extract_tag(text: str, tag: str) -> str:
    match = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
    if not match:
        return ""
    return _unescape_ofx_text(match.group(1).strip())


def _escape_ofx_text(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _unescape_ofx_text(value: str) -> str:
    return (
        value.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
    )


def _format_amount(amount: Decimal) -> str:
    normalized = amount.quantize(Decimal("0.01"))
    return format(normalized, "f")


def _fitid(transaction: Transaction, index: int) -> str:
    key = (
        f"{index}|{transaction.date}|{transaction.amount}|"
        f"{transaction.name}|{transaction.memo}|{transaction.trn_type}"
    )
    return hashlib.sha256(key.encode()).hexdigest()[:16]
