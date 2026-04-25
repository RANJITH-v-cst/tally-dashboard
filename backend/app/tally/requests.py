"""XML request envelopes for the Tally HTTP/XML gateway.

These envelopes match the format documented in Tally's Developer Reference
(``https://help.tallysolutions.com``). Dates are always ``YYYYMMDD``.
"""
from __future__ import annotations

from datetime import date
from xml.sax.saxutils import escape


def _fmt_date(d: date | None) -> str:
    return d.strftime("%Y%m%d") if d else ""


def _wrap(
    request_type: str,
    request_id: str,
    static_variables: dict[str, str] | None = None,
    tdl: str = "",
) -> str:
    sv = ""
    if static_variables:
        sv_inner = "".join(
            f"<{k}>{escape(v)}</{k}>" for k, v in static_variables.items() if v != ""
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


def list_companies() -> str:
    return _wrap("Collection", "List of Companies")


def company_info(company: str) -> str:
    return _wrap(
        "Function",
        "$$CurrentCompany",
        {"SVCURRENTCOMPANY": company},
    )


def day_book(from_date: date, to_date: date, company: str = "") -> str:
    return _wrap(
        "Data",
        "Day Book",
        {
            "SVEXPORTFORMAT": "$$SysName:XML",
            "SVFROMDATE": _fmt_date(from_date),
            "SVTODATE": _fmt_date(to_date),
            "SVCURRENTCOMPANY": company,
        },
    )


def ledgers() -> str:
    tdl = (
        "<TDL>"
        "<TDLMESSAGE>"
        '<COLLECTION ISMODIFY="No" NAME="DashboardLedgers">'
        "<TYPE>Ledger</TYPE>"
        "<FETCH>Name, Parent, OpeningBalance, ClosingBalance</FETCH>"
        "</COLLECTION>"
        "</TDLMESSAGE>"
        "</TDL>"
    )
    return _wrap("Collection", "DashboardLedgers", tdl=tdl)


def stock_summary(company: str = "") -> str:
    return _wrap(
        "Data",
        "Stock Summary",
        {
            "SVEXPORTFORMAT": "$$SysName:XML",
            "SVCURRENTCOMPANY": company,
        },
    )


def trial_balance(from_date: date, to_date: date, company: str = "") -> str:
    return _wrap(
        "Data",
        "Trial Balance",
        {
            "SVEXPORTFORMAT": "$$SysName:XML",
            "SVFROMDATE": _fmt_date(from_date),
            "SVTODATE": _fmt_date(to_date),
            "SVCURRENTCOMPANY": company,
        },
    )


def profit_loss(from_date: date, to_date: date, company: str = "") -> str:
    return _wrap(
        "Data",
        "Profit & Loss",
        {
            "SVEXPORTFORMAT": "$$SysName:XML",
            "SVFROMDATE": _fmt_date(from_date),
            "SVTODATE": _fmt_date(to_date),
            "SVCURRENTCOMPANY": company,
        },
    )


def balance_sheet(as_of: date, company: str = "") -> str:
    return _wrap(
        "Data",
        "Balance Sheet",
        {
            "SVEXPORTFORMAT": "$$SysName:XML",
            "SVTODATE": _fmt_date(as_of),
            "SVCURRENTCOMPANY": company,
        },
    )


def outstanding_receivables(as_of: date, company: str = "") -> str:
    return _wrap(
        "Data",
        "Bills Receivable",
        {
            "SVEXPORTFORMAT": "$$SysName:XML",
            "SVTODATE": _fmt_date(as_of),
            "SVCURRENTCOMPANY": company,
        },
    )


def outstanding_payables(as_of: date, company: str = "") -> str:
    return _wrap(
        "Data",
        "Bills Payable",
        {
            "SVEXPORTFORMAT": "$$SysName:XML",
            "SVTODATE": _fmt_date(as_of),
            "SVCURRENTCOMPANY": company,
        },
    )
