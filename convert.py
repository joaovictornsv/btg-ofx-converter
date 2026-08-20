#!/usr/bin/env python3
"""Convert BTG Pactual bank exports to OFX format."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from fatura import parse_fatura
from guide import write_guide_copy
from ofx import write_ofx
from xls import parse_xls


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert BTG Pactual bank exports to OFX.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    checking = subparsers.add_parser(
        "checking",
        help="Convert a checking-account .xls extrato to OFX",
    )
    checking.add_argument(
        "input_file",
        type=Path,
        help="Path to a BTG .xls checking export",
    )

    card = subparsers.add_parser(
        "card",
        help="Convert a credit card .xlsx fatura to OFX",
    )
    card.add_argument(
        "input_file",
        type=Path,
        help="Path to a BTG .xlsx card fatura export",
    )

    return parser


def _convert(
    path: Path,
    *,
    expected_suffix: str,
    parse,
    acct_type: str,
) -> int:
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    suffix = path.suffix.lower()
    if suffix != expected_suffix:
        print(
            f"Error: unsupported format '{suffix}'. Expected: {expected_suffix}",
            file=sys.stderr,
        )
        return 1

    try:
        period_start, period_end, transactions = parse(path)
    except ImportError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: failed to read {path}: {exc}", file=sys.stderr)
        return 1

    output_path = path.with_suffix(".ofx")
    output_path.write_text(
        write_ofx(period_start, period_end, transactions, acct_type=acct_type),
        encoding="utf-8",
    )
    write_guide_copy(path.parent)
    print(f"OFX written to {output_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path: Path = args.input_file

    if args.command == "checking":
        return _convert(
            path,
            expected_suffix=".xls",
            parse=parse_xls,
            acct_type="CHECKING",
        )

    if args.command == "card":
        return _convert(
            path,
            expected_suffix=".xlsx",
            parse=parse_fatura,
            acct_type="CREDITCARD",
        )

    print(f"Error: unknown command: {args.command}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
