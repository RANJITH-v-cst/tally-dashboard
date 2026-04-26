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
    if isinstance(value, dict):
        # xmltodict represents elements with attributes as a dict whose text
        # is under '#text'.
        return to_float(value.get("#text"))
    text_ = str(value).strip()
    if not text_:
        return 0.0
    sign = 1.0
    upper = text_.upper()
    if upper.endswith(" CR") or upper.endswith("CR"):
        sign = -1.0
    text_ = text_.replace(",", "")
    match = _NUMBER_RE.search(text_)
    if not match:
        return 0.0
    return sign * float(match.group(0))


def to_date(value: Any) -> date | None:
    if not value:
        return None
    text_ = str(value).strip()
    for fmt in ("%Y%m%d", "%d-%b-%Y", "%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text_, fmt).date()
        except ValueError:
            continue
    return None


def text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        # xmltodict stores element text under '#text' when attrs are present
        return str(value.get("#text", "")).strip()
    if isinstance(value, list) and value:
        return text(value[0])
    return str(value).strip()


def _walk(node: Any, key: str) -> list[Any]:
    """Recursively collect every value under ``key`` anywhere inside ``node``.

    Useful because Tally responses wrap collections at different depths
    depending on the request type — e.g. ``ENVELOPE/COLLECTION/COMPANY``
    vs ``ENVELOPE/BODY/DATA/COLLECTION/COMPANY`` vs ``ENVELOPE/COMPANY``.
    """
    found: list[Any] = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k == key:
                found.extend(as_list(v))
            else:
                found.extend(_walk(v, key))
    elif isinstance(node, list):
        for item in node:
            found.extend(_walk(item, key))
    return found


def _name_of(item: Any) -> str:
    """Return the NAME of a Tally entity, handling all common shapes."""
    if not isinstance(item, dict):
        return text(item)
    # Plain attribute on the parent element: <COMPANY NAME="ACME">...
    name_attr = item.get("@NAME")
    if name_attr:
        return text(name_attr)
    # <NAME>ACME</NAME>
    if "NAME" in item:
        return text(item["NAME"])
    # <LANGUAGENAME.LIST><NAME.LIST><NAME>ACME</NAME></NAME.LIST></LANGUAGENAME.LIST>
    lang = item.get("LANGUAGENAME.LIST")
    if isinstance(lang, dict):
        name_list = lang.get("NAME.LIST")
        if isinstance(name_list, dict):
            return text(name_list.get("NAME"))
    return ""


# ---------------------------------------------------------------------------
# Companies
# ---------------------------------------------------------------------------


def parse_companies(payload: dict) -> list[str]:
    names: list[str] = []
    for item in _walk(payload, "COMPANY"):
        n = _name_of(item)
        if n and n not in names:
            names.append(n)
    return names


def parse_companies_full(payload: dict) -> list[dict]:
    """Same as parse_companies but with the structured fields TallyPrime returns."""
    out: list[dict] = []
    for item in _walk(payload, "COMPANY"):
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "name": _name_of(item),
                "starting_from": to_date(item.get("STARTINGFROM")),
                "books_from": to_date(item.get("BOOKSFROM")),
                "state": text(item.get("STATENAME")),
                "formal_name": text(item.get("FORMALNAME")),
            }
        )
    return out


# ---------------------------------------------------------------------------
# Ledgers
# ---------------------------------------------------------------------------


def parse_ledgers(payload: dict) -> list[dict]:
    out: list[dict] = []
    for item in _walk(payload, "LEDGER"):
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "name": _name_of(item),
                "parent": text(item.get("PARENT")),
                "opening_balance": to_float(item.get("OPENINGBALANCE")),
                "closing_balance": to_float(item.get("CLOSINGBALANCE")),
            }
        )
    return [r for r in out if r["name"]]


def parse_groups(payload: dict) -> list[dict]:
    out: list[dict] = []
    for item in _walk(payload, "GROUP"):
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "name": _name_of(item),
                "parent": text(item.get("PARENT")),
                "primary_group": text(item.get("PRIMARYGROUP")),
                "is_reserved": text(item.get("RESERVEDNAME")) != "",
            }
        )
    return [r for r in out if r["name"]]


# ---------------------------------------------------------------------------
# Day Book / Vouchers
# ---------------------------------------------------------------------------


def parse_day_book(payload: dict) -> list[dict]:
    entries: list[dict] = []
    for voucher in _walk(payload, "VOUCHER"):
        if not isinstance(voucher, dict):
            continue
        # Sum the amount from the inventory or ledger entries if AMOUNT
        # is missing on the voucher header (varies by voucher type).
        amount = to_float(voucher.get("AMOUNT"))
        if not amount:
            for entry in as_list(voucher.get("ALLLEDGERENTRIES.LIST")):
                if isinstance(entry, dict):
                    a = to_float(entry.get("AMOUNT"))
                    if a > 0:
                        amount = a
                        break
        party = text(
            voucher.get("PARTYLEDGERNAME")
            or voucher.get("PARTYNAME")
            or voucher.get("BASICBUYERNAME")
        )
        entries.append(
            {
                "date": to_date(voucher.get("DATE")) or date.today(),
                "voucher_number": text(voucher.get("VOUCHERNUMBER")),
                "voucher_type": text(
                    voucher.get("VOUCHERTYPENAME")
                    or voucher.get("@VCHTYPE")
                    or voucher.get("VCHTYPE")
                ),
                "party": party,
                "amount": amount,
                "narration": text(voucher.get("NARRATION")),
            }
        )
    return entries


# ---------------------------------------------------------------------------
# Stock
# ---------------------------------------------------------------------------


def parse_stock_summary(payload: dict) -> list[dict]:
    items: list[dict] = []
    for item in _walk(payload, "STOCKITEM"):
        if not isinstance(item, dict):
            continue
        items.append(
            {
                "name": _name_of(item),
                "quantity": to_float(
                    item.get("CLOSINGBALANCE") or item.get("QUANTITY")
                ),
                "unit": text(item.get("BASEUNITS") or item.get("UNIT")),
                "rate": to_float(item.get("CLOSINGRATE") or item.get("RATE")),
                "value": to_float(item.get("CLOSINGVALUE") or item.get("VALUE")),
            }
        )
    return [s for s in items if s["name"]]


# ---------------------------------------------------------------------------
# Trial Balance
# ---------------------------------------------------------------------------


def parse_trial_balance(payload: dict) -> list[dict]:
    """Trial Balance is a hierarchical report. We flatten the leaf rows.

    TallyPrime returns entries shaped like::

        <DSPACCNAME>
          <DSPDISPNAME>Sales Account</DSPDISPNAME>
          <DSPACCINFO>
            <DSPCLDRAMT><DSPCLDRAMTA>1,00,000.00 Dr</DSPCLDRAMTA></DSPCLDRAMT>
            <DSPCLCRAMT><DSPCLCRAMTA>0</DSPCLCRAMTA></DSPCLCRAMT>
          </DSPACCINFO>
        </DSPACCNAME>
    """
    rows: list[dict] = []
    for group in _walk(payload, "DSPACCNAME"):
        if not isinstance(group, dict):
            continue
        name = text(group.get("DSPDISPNAME") or group.get("NAME"))
        info = group.get("DSPACCINFO") or {}
        if not isinstance(info, dict):
            info = {}
        debit_node = info.get("DSPCLDRAMT") or {}
        credit_node = info.get("DSPCLCRAMT") or {}
        debit = to_float(
            debit_node.get("DSPCLDRAMTA") if isinstance(debit_node, dict) else debit_node
        )
        credit = to_float(
            credit_node.get("DSPCLCRAMTA") if isinstance(credit_node, dict) else credit_node
        )
        if name:
            rows.append({"name": name, "parent": "", "debit": debit, "credit": credit})
    return rows
