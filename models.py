"""Data types for bank transactions."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Transaction:
    trn_type: str
    date: str
    amount: Decimal
    memo: str
    name: str
    source: str = ""
