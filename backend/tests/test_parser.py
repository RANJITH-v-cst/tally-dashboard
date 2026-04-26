"""Tests for the Tally XML parsers using realistic TallyPrime payloads."""
from __future__ import annotations

from datetime import date

import xmltodict

from app.tally import parser


def _parse(xml: str) -> dict:
    return xmltodict.parse(xml)


def test_parse_companies_with_attributes() -> None:
    xml = """<ENVELOPE>
      <COMPANY NAME="ACME PVT LTD">
        <STARTINGFROM>20240401</STARTINGFROM>
        <BOOKSFROM>20240401</BOOKSFROM>
        <STATENAME>Karnataka</STATENAME>
      </COMPANY>
      <COMPANY NAME="BETA TRADERS">
        <STARTINGFROM>20230401</STARTINGFROM>
      </COMPANY>
    </ENVELOPE>"""
    assert parser.parse_companies(_parse(xml)) == ["ACME PVT LTD", "BETA TRADERS"]


def test_parse_companies_with_collection_wrapper() -> None:
    xml = """<ENVELOPE><BODY><DATA><COLLECTION>
      <COMPANY><NAME>Single Co</NAME></COMPANY>
    </COLLECTION></DATA></BODY></ENVELOPE>"""
    assert parser.parse_companies(_parse(xml)) == ["Single Co"]


def test_parse_companies_full_returns_dates_and_state() -> None:
    xml = """<ENVELOPE><COMPANY NAME="X">
      <STARTINGFROM>20240401</STARTINGFROM>
      <BOOKSFROM>20240401</BOOKSFROM>
      <STATENAME>Tamil Nadu</STATENAME>
    </COMPANY></ENVELOPE>"""
    rows = parser.parse_companies_full(_parse(xml))
    assert rows[0]["name"] == "X"
    assert rows[0]["starting_from"] == date(2024, 4, 1)
    assert rows[0]["state"] == "Tamil Nadu"


def test_parse_ledgers_handles_dr_cr_and_commas() -> None:
    xml = """<ENVELOPE><BODY><DATA><COLLECTION>
      <LEDGER NAME="Cash"><PARENT>Cash-in-hand</PARENT>
        <OPENINGBALANCE>10,000.00 Dr</OPENINGBALANCE>
        <CLOSINGBALANCE>1,25,000.50 Dr</CLOSINGBALANCE>
      </LEDGER>
      <LEDGER NAME="ABC"><PARENT>Sundry Debtors</PARENT>
        <OPENINGBALANCE>0</OPENINGBALANCE>
        <CLOSINGBALANCE>50,000 Cr</CLOSINGBALANCE>
      </LEDGER>
    </COLLECTION></DATA></BODY></ENVELOPE>"""
    rows = parser.parse_ledgers(_parse(xml))
    assert rows[0]["name"] == "Cash"
    assert rows[0]["closing_balance"] == 125000.5
    assert rows[1]["closing_balance"] == -50000.0  # Cr → negative


def test_parse_day_book_extracts_voucher_fields() -> None:
    xml = """<ENVELOPE><BODY><DATA><TALLYMESSAGE>
      <VOUCHER VCHTYPE="Sales">
        <DATE>20250410</DATE>
        <VOUCHERNUMBER>SI-001</VOUCHERNUMBER>
        <VOUCHERTYPENAME>Sales</VOUCHERTYPENAME>
        <PARTYLEDGERNAME>ABC Corp</PARTYLEDGERNAME>
        <AMOUNT>5,000.00 Cr</AMOUNT>
        <NARRATION>Inv #1</NARRATION>
      </VOUCHER>
    </TALLYMESSAGE></DATA></BODY></ENVELOPE>"""
    rows = parser.parse_day_book(_parse(xml))
    assert rows[0]["date"] == date(2025, 4, 10)
    assert rows[0]["voucher_number"] == "SI-001"
    assert rows[0]["voucher_type"] == "Sales"
    assert rows[0]["party"] == "ABC Corp"
    assert rows[0]["amount"] == -5000.0


def test_parse_stock_summary_extracts_value() -> None:
    xml = """<ENVELOPE><BODY><DATA><COLLECTION>
      <STOCKITEM NAME="Widget">
        <BASEUNITS>nos</BASEUNITS>
        <CLOSINGBALANCE>100 nos</CLOSINGBALANCE>
        <CLOSINGRATE>50/nos</CLOSINGRATE>
        <CLOSINGVALUE>5,000.00</CLOSINGVALUE>
      </STOCKITEM>
    </COLLECTION></DATA></BODY></ENVELOPE>"""
    rows = parser.parse_stock_summary(_parse(xml))
    assert rows[0]["name"] == "Widget"
    assert rows[0]["value"] == 5000.0


def test_parse_trial_balance_dspaccname() -> None:
    xml = """<ENVELOPE><BODY><DATA>
      <DSPACCNAME>
        <DSPDISPNAME>Sales Account</DSPDISPNAME>
        <DSPACCINFO>
          <DSPCLDRAMT><DSPCLDRAMTA>0</DSPCLDRAMTA></DSPCLDRAMT>
          <DSPCLCRAMT><DSPCLCRAMTA>1,00,000.00 Cr</DSPCLCRAMTA></DSPCLCRAMT>
        </DSPACCINFO>
      </DSPACCNAME>
    </DATA></BODY></ENVELOPE>"""
    rows = parser.parse_trial_balance(_parse(xml))
    assert rows[0]["name"] == "Sales Account"
    assert rows[0]["credit"] == -100000.0


def test_to_float_handles_edge_cases() -> None:
    assert parser.to_float(None) == 0.0
    assert parser.to_float("") == 0.0
    assert parser.to_float("not a number") == 0.0
    assert parser.to_float("1,00,000") == 100000.0
    assert parser.to_float("100 Dr") == 100.0
    assert parser.to_float("100 Cr") == -100.0
    assert parser.to_float({"#text": "42"}) == 42.0
