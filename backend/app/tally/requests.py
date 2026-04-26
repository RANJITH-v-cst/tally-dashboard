"""XML request envelopes for the Tally HTTP/XML gateway.

These envelopes match the format documented in Tally's Developer Reference
(``https://help.tallysolutions.com``). Dates are always ``YYYYMMDD``.

Where possible we define the collection inline with a `<TDL><COLLECTION>`
block and a `<FETCH>` list. This is more reliable across TallyPrime
versions than relying on the gateway's default named reports.
"""
from __future__ import annotations

from datetime import date
from xml.sax.saxutils import escape


def _fmt_date(d: date | None) -> str:
    return d.strftime("%Y%m%d") if d else ""


def _envelope(
    request_type: str,
    request_id: str,
    static_variables: dict[str, str] | None = None,
    tdl: str = "",
) -> str:
    sv = ""
    if static_variables:
        sv_inner = "".join(
            f"<{k}>{escape(v)}</{k}>"
            for k, v in static_variables.items()
            if v != ""
        )
        sv = f"<STATICVARIABLES>{sv_inner}</STATICVARIABLES>"
    return (
        "<ENVELOPE>"
        "<HEADER>"
        "<VERSION>1</VERSION>"
        "<TALLYREQUEST>Export</TALLYREQUEST>"
        f"<TYPE>{escape(request_type)}</TYPE>"
        f"<ID>{escape(request_id)}</ID>"
        "</HEADER>"
        "<BODY>"
        "<DESC>"
        f"{sv}"
        f"{tdl}"
        "</DESC>"
        "</BODY>"
        "</ENVELOPE>"
    )


def _collection(
    name: str,
    type_: str,
    fetch: list[str],
    extra: str = "",
    static_variables: dict[str, str] | None = None,
) -> str:
    """Build a request that defines an inline collection and exports it."""
    fetch_xml = ",".join(fetch)
    tdl = (
        "<TDL>"
        "<TDLMESSAGE>"
        f'<COLLECTION NAME="{name}" ISMODIFY="No" ISFIXED="No" '
        'ISINITIALIZE="No" ISOPTION="No" ISINTERNAL="No">'
        f"<TYPE>{type_}</TYPE>"
        f"<FETCH>{fetch_xml}</FETCH>"
        f"{extra}"
        "</COLLECTION>"
        "</TDLMESSAGE>"
        "</TDL>"
    )
    sv = {"SVEXPORTFORMAT": "$$SysName:XML"}
    if static_variables:
        sv.update(static_variables)
    return _envelope("Collection", name, sv, tdl)


# ---------------------------------------------------------------------------
# Companies
# ---------------------------------------------------------------------------


def list_companies() -> str:
    """All companies the running Tally instance knows about (loaded or not)."""
    return _collection(
        "DashListOfCompanies",
        "Company",
        ["NAME", "STARTINGFROM", "BOOKSFROM", "STATENAME", "FORMALNAME"],
    )


def loaded_companies() -> str:
    """Only companies that are currently *loaded* (open) in Tally."""
    return _collection(
        "DashLoadedCompanies",
        "Company",
        ["NAME", "STARTINGFROM", "BOOKSFROM", "STATENAME", "FORMALNAME"],
        extra="<FILTER>IsLoaded</FILTER>"
        "<SYSTEM TYPE=\"Formulae\" NAME=\"IsLoaded\">$$IsCmpLoaded:$NAME</SYSTEM>",
    )


# ---------------------------------------------------------------------------
# Day Book (vouchers within a date range)
# ---------------------------------------------------------------------------


def day_book(from_date: date, to_date: date, company: str = "") -> str:
    sv: dict[str, str] = {
        "SVEXPORTFORMAT": "$$SysName:XML",
        "SVFROMDATE": _fmt_date(from_date),
        "SVTODATE": _fmt_date(to_date),
    }
    if company:
        sv["SVCURRENTCOMPANY"] = company
    return _envelope("Data", "Day Book", sv)


# ---------------------------------------------------------------------------
# Ledgers
# ---------------------------------------------------------------------------


def ledgers(company: str = "") -> str:
    sv = {"SVCURRENTCOMPANY": company} if company else None
    return _collection(
        "DashLedgers",
        "Ledger",
        [
            "NAME",
            "PARENT",
            "OPENINGBALANCE",
            "CLOSINGBALANCE",
            "MAILINGNAME",
            "GSTREGISTRATIONTYPE",
            "PARTYGSTIN",
        ],
        static_variables=sv,
    )


def groups(company: str = "") -> str:
    sv = {"SVCURRENTCOMPANY": company} if company else None
    return _collection(
        "DashGroups",
        "Group",
        ["NAME", "PARENT", "PRIMARYGROUP", "RESERVEDNAME"],
        static_variables=sv,
    )


# ---------------------------------------------------------------------------
# Stock
# ---------------------------------------------------------------------------


def stock_items(company: str = "") -> str:
    sv = {"SVCURRENTCOMPANY": company} if company else None
    return _collection(
        "DashStockItems",
        "StockItem",
        [
            "NAME",
            "PARENT",
            "BASEUNITS",
            "OPENINGBALANCE",
            "OPENINGRATE",
            "OPENINGVALUE",
            "CLOSINGBALANCE",
            "CLOSINGRATE",
            "CLOSINGVALUE",
        ],
        static_variables=sv,
    )


def stock_summary(company: str = "") -> str:
    sv: dict[str, str] = {"SVEXPORTFORMAT": "$$SysName:XML"}
    if company:
        sv["SVCURRENTCOMPANY"] = company
    return _envelope("Data", "Stock Summary", sv)


# ---------------------------------------------------------------------------
# Trial Balance / P&L / Balance Sheet (built-in reports)
# ---------------------------------------------------------------------------


def trial_balance(from_date: date, to_date: date, company: str = "") -> str:
    sv: dict[str, str] = {
        "SVEXPORTFORMAT": "$$SysName:XML",
        "SVFROMDATE": _fmt_date(from_date),
        "SVTODATE": _fmt_date(to_date),
    }
    if company:
        sv["SVCURRENTCOMPANY"] = company
    return _envelope("Data", "Trial Balance", sv)


def profit_loss(from_date: date, to_date: date, company: str = "") -> str:
    sv: dict[str, str] = {
        "SVEXPORTFORMAT": "$$SysName:XML",
        "SVFROMDATE": _fmt_date(from_date),
        "SVTODATE": _fmt_date(to_date),
    }
    if company:
        sv["SVCURRENTCOMPANY"] = company
    return _envelope("Data", "Profit & Loss", sv)


def balance_sheet(as_of: date, company: str = "") -> str:
    sv: dict[str, str] = {
        "SVEXPORTFORMAT": "$$SysName:XML",
        "SVTODATE": _fmt_date(as_of),
    }
    if company:
        sv["SVCURRENTCOMPANY"] = company
    return _envelope("Data", "Balance Sheet", sv)


def outstanding_receivables(as_of: date, company: str = "") -> str:
    sv: dict[str, str] = {
        "SVEXPORTFORMAT": "$$SysName:XML",
        "SVTODATE": _fmt_date(as_of),
    }
    if company:
        sv["SVCURRENTCOMPANY"] = company
    return _envelope("Data", "Bills Receivable", sv)


def outstanding_payables(as_of: date, company: str = "") -> str:
    sv: dict[str, str] = {
        "SVEXPORTFORMAT": "$$SysName:XML",
        "SVTODATE": _fmt_date(as_of),
    }
    if company:
        sv["SVCURRENTCOMPANY"] = company
    return _envelope("Data", "Bills Payable", sv)
