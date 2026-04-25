"""Parsers for Tally XML responses.

Tally XML is famously inconsistent — element names are upper-case with no
namespace, repeated elements are sometimes a list and sometimes a single
dict (when only one instance exists), and numeric values come as strings
that may contain commas, trailing ``Dr``/``Cr`` markers, or be empty.

The helpers here normalise those quirks.
"""
from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")


def to_float(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return 0.0
    sign = 1.0
    # Tally uses "Dr" (debit, positive) and "Cr" (credit, negative) suffixes
    upper = text.upper()
    if upper.endswith(" CR") or upper.endswith("CR"):
        sign = -1.0
    text = text.replace(",", "")
    match = _NUMBER_RE.search(text)
    if not match:
        return 0.0
    return sign * float(match.group(0))


def to_date(value: Any) -> date | None:
    if not value:
        return None
    text = str(value).strip()
    for fmt in ("%Y%m%d", "%d-%b-%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        # xmltodict stores element text under '#text' when attrs are present
        return str(value.get("#text", "")).strip()
    return str(value).strip()


def parse_companies(payload: dict) -> list[str]:
    envelope = payload.get("ENVELOPE", payload)
    names: list[str] = []
    for item in as_list(envelope.get("COMPANY")):
        name = text(item.get("NAME") if isinstance(item, dict) else item)
        if name:
            names.append(name)
    # Some Tally versions wrap companies in COLLECTION/COMPANY
    if not names:
        collection = envelope.get("COLLECTION") or {}
        for item in as_list(collection.get("COMPANY")):
            name = text(item.get("NAME") if isinstance(item, dict) else item)
            if name:
                names.append(name)
    return names


def parse_ledgers(payload: dict) -> list[dict]:
    envelope = payload.get("ENVELOPE", payload)
    collection = envelope.get("COLLECTION") or envelope.get("BODY", {}).get("DATA", {})
    ledgers: list[dict] = []
    for item in as_list(collection.get("LEDGER") if isinstance(collection, dict) else None):
        if not isinstance(item, dict):
            continue
        ledgers.append(
            {
                "name": text(item.get("@NAME") or item.get("NAME") or item.get("LANGUAGENAME.LIST", {})),
                "parent": text(item.get("PARENT")),
                "opening_balance": to_float(item.get("OPENINGBALANCE")),
                "closing_balance": to_float(item.get("CLOSINGBALANCE")),
            }
        )
    return ledgers


def parse_day_book(payload: dict) -> list[dict]:
    envelope = payload.get("ENVELOPE", payload)
    body = envelope.get("BODY") or {}
    data = body.get("DATA") if isinstance(body, dict) else None
    vouchers_root = data or envelope
    entries: list[dict] = []
    for voucher in as_list(vouchers_root.get("VOUCHER") if isinstance(vouchers_root, dict) else None):
        if not isinstance(voucher, dict):
            continue
        party = text(voucher.get("PARTYLEDGERNAME") or voucher.get("PARTYNAME"))
        entries.append(
            {
                "date": to_date(voucher.get("DATE")) or date.today(),
                "voucher_number": text(voucher.get("VOUCHERNUMBER")),
                "voucher_type": text(voucher.get("VOUCHERTYPENAME") or voucher.get("@VCHTYPE")),
                "party": party,
                "amount": to_float(voucher.get("AMOUNT")),
                "narration": text(voucher.get("NARRATION")),
            }
        )
    return entries


def parse_stock_summary(payload: dict) -> list[dict]:
    envelope = payload.get("ENVELOPE", payload)
    items: list[dict] = []
    for item in as_list(envelope.get("STOCKITEM")):
        if not isinstance(item, dict):
            continue
        items.append(
            {
                "name": text(item.get("@NAME") or item.get("NAME")),
                "quantity": to_float(item.get("CLOSINGBALANCE") or item.get("QUANTITY")),
                "unit": text(item.get("BASEUNITS") or item.get("UNIT")),
                "rate": to_float(item.get("CLOSINGRATE") or item.get("RATE")),
                "value": to_float(item.get("CLOSINGVALUE") or item.get("VALUE")),
            }
        )
    return items


def parse_trial_balance(payload: dict) -> list[dict]:
    envelope = payload.get("ENVELOPE", payload)
    rows: list[dict] = []
    for group in as_list(envelope.get("DSPACCNAME")):
        # DSPACCNAME contains name + debit/credit totals
        if not isinstance(group, dict):
            continue
        name = text(group.get("DSPDISPNAME") or group.get("NAME"))
        debit = to_float(group.get("DSPACCINFO", {}).get("DSPCLDRAMT", {}).get("DSPCLDRAMTA"))
        credit = to_float(group.get("DSPACCINFO", {}).get("DSPCLCRAMT", {}).get("DSPCLCRAMTA"))
        rows.append({"name": name, "parent": "", "debit": debit, "credit": credit})
    return rows
